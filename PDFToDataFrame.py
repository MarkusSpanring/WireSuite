import cv2
import numpy as np
import pandas as pd
import os
import shutil
import pytesseract
import copy
import pdf2image


def save_images_from_pdf(filename):
    folder = filename.split("/")[-1].split(".")[0]
    if os.path.exists( folder ):
        shutil.rmtree(folder)
    os.makedirs(folder)

    png_images = []
    images = pdf2image.convert_from_path(filename,size=(5000,None))
    for pageIdx, image in enumerate(images):
        imagename ="{folder}/{folder}_page{pagenumber}.png".format(folder=folder,pagenumber=pageIdx)
        image.save(imagename,"PNG")
        png_images.append(imagename)
    return png_images


def find_contours_in_image(filename, debug = False):
    if debug:
        if os.path.exists( "debug" ):
            shutil.rmtree("debug")
        os.makedirs("debug")

    cv_image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    orig_image = cv2.imread(filename)

    # Thresholding the image
    (thresh, img_bin) = cv2.threshold(cv_image, 128, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # Invert the image
    img_bin = 255-img_bin 

    vertical_kernel_length = np.array(cv_image).shape[0]//25
    horizontal_kernel_length = np.array(cv_image).shape[1]//25

    # A verticle kernel of (1 X kernel_length), which will detect all the verticle lines from the image.
    verticle_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vertical_kernel_length))
    # A horizontal kernel of (kernel_length X 1), which will help to detect all the horizontal line from the image.
    hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_kernel_length, 1))
    # A kernel of (3 X 3) ones.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    # Morphological operation to detect vertical lines from an image
    img_temp1 = cv2.erode(img_bin, verticle_kernel, iterations=3)
    verticle_lines_img = cv2.dilate(img_temp1, verticle_kernel, iterations=3)


    # Morphological operation to detect horizontal lines from an image
    img_temp2 = cv2.erode(img_bin, hori_kernel, iterations=3)
    horizontal_lines_img = cv2.dilate(img_temp2, hori_kernel, iterations=3)


    # Weighting parameters, this will decide the quantity of an image to be added to make a new image.
    alpha = 0.5
    beta = 1.0 - alpha
    # This function helps to add two image with specific weight parameter to get a third image as summation of two image.
    img_final_bin = cv2.addWeighted(verticle_lines_img, alpha, horizontal_lines_img, beta, 0.0)
    img_final_bin = cv2.erode(~img_final_bin, kernel, iterations=2)
    (thresh, img_final_bin) = cv2.threshold(img_final_bin, 128,255, cv2.THRESH_BINARY)

    if debug:
        cv2.imwrite("debug/horizontal_lines.jpg",horizontal_lines_img)
        cv2.imwrite("debug/verticle_lines.jpg",verticle_lines_img)
        cv2.imwrite("debug/img_final_bin.jpg",img_final_bin)

    # Find contours for image, which will detect all the boxes
    contours, hierarchy = cv2.findContours(img_final_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #remove parents if children are available
    individual_contours = []
    for i,h in enumerate(hierarchy[0]):
        if h[2] == -1:
            individual_contours.append( contours[i])
    # contours = individual_contours

    if debug:

        cont_img = copy.deepcopy(orig_image)
        cv2.drawContours(cont_img, contours, -1, (0, 0, 255), 2)
        cv2.imwrite("debug/boxes.jpg",cont_img)

    return orig_image, contours

def sort_and_convert_contours(cnts):

    # construct the list of bounding boxes and sort them from left to right and top to
    # bottom

    boundingBoxes = pd.DataFrame([cv2.boundingRect(c) for c in cnts ], columns = list('xywh'))
    # return the list of sorted contours and bounding boxes
    sorted_boxes = boundingBoxes.sort_values(by=['x','y'],ascending=[True,True])


    return sorted_boxes.reset_index(drop=True)

def reduce_boxes(bndboxes):

    edge_count_x = bndboxes["x"].value_counts().to_dict()
    edge_count_y = bndboxes["y"].value_counts().to_dict()

    reduced_boxes = bndboxes.assign(freq_x=bndboxes.apply(lambda x: edge_count_x[ x["x"] ], axis=1) )
    reduced_boxes = reduced_boxes.assign(freq_y=reduced_boxes.apply(lambda x: edge_count_y[ x["y"] ], axis=1) )

    reduced_boxes["area"] = reduced_boxes["w"]*reduced_boxes["h"]

    main_area = float(reduced_boxes.iloc[0]["area"])
    reduced_boxes = reduced_boxes[ reduced_boxes["area"] / main_area < 0.85   ]


    #remove artefacts and large structures
    # reduced_boxes = reduced_boxes[ (reduced_boxes["freq_x"] * reduced_boxes["freq_y"]) > 6  ]
    reduced_boxes = reduced_boxes[ (reduced_boxes["w"] > 10) & (reduced_boxes["h"] > 10) ]
    # reduced_boxes.drop([0],inplace=True)

    return reduced_boxes.drop(["freq_x","freq_y","area"],axis=1).reset_index(drop=True)

class BoxCluster():

    def __init__(self, tolerance=12):
        self.tolerance = tolerance
        self._cluster_empty = True
        self._id_cluster = np.full((100,50), -1)
        self._box_cluster = np.full((100,50), None)
        self._ocr_cluster = np.full((100,50), None)
        self.image = None


    def used_indices(self):
        used = np.where(self._id_cluster > -1)
        return zip(used[0],used[1])

    def get_cluster_box(self, box_coordinates = "relative"):
        if self._cluster_empty:
            return (0,0,0,0)

        first = True
        cluster_box = [0,0,0,0]
        for x,y in self.used_indices():
            box = self._box_cluster[x,y]
            if first:
                first = False
                cluster_box[0] = box["x"]
                cluster_box[1] = box["y"]
                cluster_box[2] = box["x"] + box["w"]
                cluster_box[3] = box["y"] + box["h"]
            else:
                cluster_box[0] = min( cluster_box[0],box["x"] )
                cluster_box[1] = min( cluster_box[1],box["y"] )
                cluster_box[2] = max( cluster_box[2], box["x"]+box["w"] )
                cluster_box[3] = max( cluster_box[3], box["y"]+box["h"] )

        if box_coordinates == "relative":
            cluster_box[2] = cluster_box[2] - cluster_box[0]
            cluster_box[3] = cluster_box[3] - cluster_box[1]
            return pd.DataFrame( [cluster_box], columns=list("xywh") ).iloc[0]

        if box_coordinates == "absolute":
            return pd.DataFrame( [cluster_box], columns=["x1","y1","x2","y2"] ).iloc[0]


    def set_image_file(self, image):
        self.image = copy.deepcopy(image)

    def crop_image_to_box(self, box, outfolder):
        x = slice( box["x"], box["x"] + box["w"] )
        y = slice( box["y"], box["y"] + box["h"] )

        filename = "{outfolder}/box_at_x{x}_y{y}.png".format(x=box["x"],y=box["y"],
                                                             outfolder=outfolder)

        new_img = self.image[y, x]
        cv2.imwrite(filename, new_img)

        return filename


    def extract_data_in_box(self, box):
        x = slice( box["x"], box["x"] + box["w"] )
        y = slice( box["y"], box["y"] + box["h"] )

        new_img = self.image[y, x]
        data = [elm for elm in pytesseract.image_to_string(new_img).splitlines() if elm]
        return data

    def extract_data_in_cluster(self, debug = False, outfolder = ""):

        for i,j in self.used_indices():
            box = self._box_cluster[i,j]
            if debug:
                self.crop_image_to_box(box, outfolder)
            self._ocr_cluster[i,j] = self.extract_data_in_box(box)

        self.flatten_and_check_ocr_cluster()

    def flatten_and_check_ocr_cluster(self):

        rows,cols = self._ocr_cluster.shape

        for row in range(rows):
            subrows = 0
            # check if all columns have the same size.
            # Use the largest number of entries otherwise
            for col in range(cols):
                if self._ocr_cluster[row,col] is None:
                    self._ocr_cluster[row,col] = []*subrows
                subrows = max(len(self._ocr_cluster[row,col]), subrows)


            for col in range(cols):
                to_add = subrows - len(self._ocr_cluster[row,col])
                if to_add != 0:
                    for i in range(to_add):
                        self._ocr_cluster[row,col].append("#CHECK#")

    def get_table_as_dataframe(self):
        rows,cols = self._ocr_cluster.shape

        reshaped_cluster = []
        for row in range(rows):
            subrows = len(self._ocr_cluster[row,0])
            for subrow in range(subrows):
                tmp_row = []
                for col in range(cols):
                    tmp_row.append(self._ocr_cluster[row,col][subrow].replace("|","\t"))
                reshaped_cluster.append(tmp_row)

        return pd.DataFrame(reshaped_cluster)



    def build_a_cluster_from(self, bndboxes):
        old_cluster_size = 0

        for i in range(3):
            new_cluster_size = self.clustering(bndboxes)
            if new_cluster_size == old_cluster_size:
                break
            old_cluster_size = new_cluster_size

        col_mask = np.all( np.equal(self._id_cluster, -1), axis=0)
        self._id_cluster = self._id_cluster[:,~col_mask]
        self._box_cluster = self._box_cluster[:,~col_mask]
        self._ocr_cluster = self._ocr_cluster[:,~col_mask]

        row_mask = np.all( np.equal(self._id_cluster, -1), axis=1)
        self._id_cluster = self._id_cluster[~row_mask]
        self._box_cluster = self._box_cluster[~row_mask]
        self._ocr_cluster = self._ocr_cluster[~row_mask]

        return [box_id for box_id in self._id_cluster.flatten() if box_id != -1]

    def clustering(self, bndboxes):

        idx = -1
        idy = -1
        for box_id in bndboxes.index:
            box = bndboxes.loc[box_id]
            if not self.box_in_cluster(box_id):
                if self._cluster_empty:
                    self._cluster_empty = False
                    idx = 0
                    idy = 0
                else:
                    idx, idy = self.find_matching_edge(box,box_id)
            else:
                continue

            if idx != -1 and idy != -1:
                self._id_cluster[idx,idy] = box_id
                self._box_cluster[idx,idy] = box

        return self._box_cluster.size

    def find_matching_edge(self, box,box_id=-1):

        vertical_match = False
        horizontal_match = False

        for x,y in self.used_indices():
            if self._id_cluster[x+1,y] != -1 and self._id_cluster[x,y+1] != -1:
                continue
            elm = self._box_cluster[x,y]

            if elm["x"] == box["x"]:
                vertical_match = abs( (elm["y"]+elm["h"]) - box["y"] ) < self.tolerance

            if elm["y"] == box["y"]:
                horizontal_match = abs( (elm["x"]+elm["w"]) - box["x"] ) < self.tolerance
            if vertical_match and self._id_cluster[x+1,y] == -1:
                return x+1, y

            if horizontal_match and self._id_cluster[x,y+1] == -1:
                return x, y+1

        return -1, -1

    def box_in_cluster(self,box_id):

        (row_loc, col_loc) = np.where(self._id_cluster == box_id)
        if row_loc.size == 0 and col_loc.size == 0:
            return ()
        return (row_loc[0], col_loc[0])

class BoxClusters():

    def __init__(self, main_image, outfolder=""):
        self.main_image = main_image
        self.outfolder = outfolder
        self.clusters = []

    def size(self):
        return len(self.clusters)

    def build_clusters(self, contours):

        bounding_boxes = sort_and_convert_contours(contours)
        bounding_boxes = reduce_boxes(bounding_boxes)

        while not bounding_boxes.empty:

            self.clusters.append(BoxCluster())
            self.clusters[-1].set_image_file(self.main_image)
            box_ids = self.clusters[-1].build_a_cluster_from(bounding_boxes)
            bounding_boxes = bounding_boxes.drop(box_ids)

        self.remove_nested_clusters()

    def remove_nested_clusters(self):
        nClusters = len(self.clusters)

        veto = []
        for i in range(nClusters):
            iCB = self.clusters[i].get_cluster_box(box_coordinates="absolute")

            for j in range(nClusters):
                if i >= j or i in veto:
                    continue

                jCB = self.clusters[j].get_cluster_box(box_coordinates="absolute")

                if jCB["x1"] < iCB["x1"] or jCB["x2"] > iCB["x2"]:
                    continue
                if jCB["y1"] < iCB["y1"] or jCB["y2"] > iCB["y2"]:
                    continue
                veto.append(i)

        good_clusters = []
        for i in range(nClusters):
            if i in veto:
                continue
            good_clusters.append(self.clusters[i])
        self.clusters = good_clusters

    def mark_clusters_in_image(self):
        marked_img = self.main_image
        for i, cluster in enumerate(self.clusters):
            cb = cluster.get_cluster_box(box_coordinates="absolute")

            cv2.rectangle(marked_img,(cb["x1"], cb["y1"]),
                                (cb["x2"], cb["y2"]),
                                color=(255, 0, 0), thickness=20)


            cv2.putText(marked_img,str(i+1), ( cb["x1"]+5, cb["y2"]-30 ),
                                cv2.FONT_HERSHEY_SIMPLEX, 10,
                                (255,0,0),20)

        outfile = self.outfolder + "/boxes.png"
        cv2.imwrite(outfile ,marked_img)
        return outfile

    def get_cluster_image(self,idx):
        cb = self.clusters[idx].get_cluster_box(box_coordinates="relative")
        return self.clusters[idx].crop_image_to_box(cb, self.outfolder)

    def get_df_from_cluster(self, idx):
        self.clusters[idx].extract_data_in_cluster()
        return self.clusters[idx].get_table_as_dataframe()


def pdf_to_dataframe(filename, page):


    png_images = save_images_from_pdf(filename=filename)
    img, contours = find_contours_in_image(png_images[page], debug = False)

    clusters = BoxClusters(img)
    clusters.build_clusters(contours=contours)
    clusters.mark_clusters_in_image()

    # return clusters[-1].get_table_as_dataframe()

def main():
    filename,page = "ED00610R46_01-DE.pdf",1
    # filename,page  = "ED00610R45_00-DE.pdf",2
    # filename,page  = "E100802R67-008.pdf",0
    # filename,page  = "ed00250r06-007.pdf",0
    # filename,page  = "E100677R01_05.pdf",0
    # filename,page  = "E100677R01_05_small.pdf",0
    pdf_to_dataframe(filename, page)




if __name__ == '__main__':
    main()
