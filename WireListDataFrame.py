import pandas as pd


def main():
    inputfile = "Drahtliste_3ED00334R26-000.xlsx"

    df = WireListDataFrame()
    df.set_dataframe_from_excel(inputfile)
    print( df.get_sorted_dataframe() )
    # df.export_to_excel("new_out",subheaders=False)

    # writeWireList(df, "test")

class WireListDataFrame():

    def __init__(self):
        self.df = pd.DataFrame([])
        self.sub_headers = []
        self.connections = [("","")]

    def set_dataframe(self,df):
        clean_df = pd.DataFrame([i for i in df.values if find_pattern(i)])
        self.df = self.add_meta(clean_df)

    def set_dataframe_from_excel(self, filename):
        raw_df = pd.read_excel(filename, sheet_name="Drahtliste")
        self.set_dataframe( raw_df.dropna(axis=1,how="all") )

    def add_meta(self,df):
        df =df.apply(define_parent_connectors, axis=1)
        self.connections = df.groupby(["start_parent","end_parent"]).count().index.to_list()

        df.fillna(value="", inplace = True)
        return df.apply(add_marker, axis=1)

    def veto(self,df):
        veto = ["marker","start_parent","end_parent","start_child","end_child"]
        cols = [c for c in self.df.columns if not c in veto]

        return df[cols]

    def get_dataframe(self, sort_rows = False, subheaders = False):
        self.sub_headers = []

        if sort_rows and subheaders:
            export_df = self._get_grouped_dataframe()
        elif sort_rows and not subheaders:
            export_df = self._get_sorted_dataframe()
        else:
            export_df = self.df

        export_df[2] = "<"
        export_df[4] = ">"
        return self.veto( export_df )

    def reorder_endpoints(self, new_connections=[]):
        for start,end in new_connections:
            for i, row in self.df.iterrows():
                if row["end_parent"] == start and row["start_parent"] == end:
                    self.df.loc[i] = switch_endpoints(row)
        self.df =self.add_meta(self.df)

    def _get_sorted_dataframe(self):
        self.sub_headers = []
        sorted_df = sort_by_connector( self.df )
        self.connections = sorted_df.groupby(["start_parent","end_parent"]).count().index.to_list()
        return sorted_df

    def _get_grouped_dataframe(self):
        sorted_df = self._get_sorted_dataframe()

        for i,row in sorted_df.iterrows():
            sub_header = row.loc["start_parent"] + " nach " + row.loc["end_parent"]
            if not self.sub_headers:
                self.sub_headers.append( (i+len(self.sub_headers),sub_header) )
            elif self.sub_headers[-1][1] != sub_header:
                self.sub_headers.append( (i+len(self.sub_headers),sub_header) )


        for i, string in self.sub_headers:
            sorted_df = insert_line(sorted_df,i,string)
        formated_df = sorted_df.fillna(value="")

        return formated_df

    def get_marker(self):
        return self.df.apply(add_marker, axis=1)

    def export_to_excel(self, filename, sort_rows = True, subheaders = True):

        if sort_rows and subheaders:
            export_df = self.get_grouped_dataframe()
        elif sort_rows and not subheaders:
            export_df = self.get_sorted_dataframe()
        else:
            export_df = self.get_dataframe()

        writer = pd.ExcelWriter(filename+'.xlsx', engine='xlsxwriter')

        export_df.to_excel(writer, sheet_name='Drahtliste',startrow=1,index=False)
        workbook  = writer.book
        worksheet = writer.sheets['Drahtliste']
        cell_format = workbook.add_format()
        cell_format.set_left(1)
        cell_format.set_right(1)

        for i,width in  enumerate( self.get_column_widths() ):
            worksheet.set_column(i, i, width,cell_format)

        top_format = workbook.add_format({'bold': 1,'border': 6, 'align': 'center'})
        top_format.set_font_size(20)
        merge_format = workbook.add_format({'bold': 1,'border': 6, 'align': 'center'})

        worksheet.merge_range('A1:J1', filename, top_format)
        for i, sub_header in self.sub_headers:
            worksheet.merge_range(i+2,0,i+2,len(self.sub_headers), sub_header, merge_format)

        writer.save()

    def get_column_widths(self):
        header = self.df.columns
        column_widths = []
        for col,name in enumerate(header):
            col_width = len( str(name) )
            individuals = self.df[name].value_counts().to_dict().keys()
            for i in individuals:
                if len(str(i)) > col_width:
                    col_width = len(str(i))
            yield col_width + 1


def writeWireList(df, filename):

    formated = WireListDataFrame(df)
    formated_df = formated.get_export_dataframe()

    writer = pd.ExcelWriter(filename+'.xlsx', engine='xlsxwriter')

    formated_df.to_excel(writer, sheet_name='Drahtliste',startrow=1,index=False)
    workbook  = writer.book
    worksheet = writer.sheets['Drahtliste']
    cell_format = workbook.add_format()
    cell_format.set_left(1)
    cell_format.set_right(1)

    for i,width in  enumerate( formated.get_column_widths() ):
        worksheet.set_column(i, i, width,cell_format)

    top_format = workbook.add_format({'bold': 1,'border': 6, 'align': 'center'})
    top_format.set_font_size(20)
    merge_format = workbook.add_format({'bold': 1,'border': 6, 'align': 'center'})

    worksheet.merge_range('A1:J1', filename, top_format)
    for i, sub_header in formated.sub_headers:
        worksheet.merge_range(i+2,0,i+2,len(formated.sub_headers), sub_header, merge_format)

    writer.save()

def sort_by_connector(df):

    modified_df = df
    if not all( [i in df.columns for i in ["start_parent","end_parent"]] ):
        modified_df = df.apply(define_parent_connectors, axis=1 )

    # Values sorted by occurrence of start parent
    start_parents = modified_df["start_parent"].value_counts().to_dict()

    index = []
    for sp in start_parents.keys():
        index += sort_by_freq( modified_df[modified_df["start_parent"] == sp], "end_parent").index.to_list()

    return modified_df.reindex(index).reset_index(drop=True)

def sort_by_freq(df, key):
    sp_count = df[key].value_counts().to_dict()
    df = df.assign(freq=df.apply(lambda x: sp_count[ x[key] ], axis=1) )
    return df.sort_values(by=['freq',key],ascending=[False,True]).drop("freq",axis=1)

def find_header(df):
    rows = df.values

    for i,row in enumerate(rows):
        if all([ label in row for label in ["von","nr.","zu"] ]):
            return list(rows[i])
    return None


def switch_endpoints(row):

    row.at[1], row.at[5] = row.at[5], row.at[1]
    row.at[0], row.at[6] = row.at[6], row.at[0]

    return row

def insert_line(df,index,string):

    line = pd.DataFrame(columns=df.columns,index=[index])
    line[df.columns[0]] = string

    return pd.concat([df.iloc[:index], line,df.iloc[index:]]).reset_index(drop=True)

def find_pattern(row):

    for i, element in enumerate(row):
        if element == "<" and row[i+2] == ">":
            return (i-1,i+1,i+3)

    for i, element in enumerate(row):

        possible_start = any([ sym in str(element) for sym in [".","X","K","S"] ])
        matching_center = False
        matching_end = False
        if possible_start:
            try:
                tmp = float(row[i+2])
            except (ValueError, IndexError) as e:
                continue
            else:
                matching_center = True

            try:
                matching_end = any([ sym in str(row[i+4]) for sym in [".","X","K","S"] ])
            except IndexError as e:
                continue

            found_one_dot = "." in str(element) + str(row[i+4])

            if all([possible_start,matching_center,matching_end,found_one_dot]):
                return (i,i+2, i+4)
    return ()

def add_marker(row):
    mpos = find_pattern(row)
    if mpos:
        row["marker"] = row[mpos[0]]+"<"+row[mpos[1]]+">"+row[mpos[2]]
    return row

def define_parent_connectors(row):
    mpos = find_pattern(row)

    splstart = row[mpos[0]].split(".")
    splend = row[mpos[2]].split(".")

    if len(splstart) > 2:
        row["start_parent"] = ".".join(splstart[:-1])
    else:
        row["start_parent"] = splstart[0]
    row["start_child"] = splstart[-1]


    if len(splstart) > 2:
        row["end_parent"] = ".".join(splend[:-1])
    else:
        row["end_parent"] = splend[0]
    row["end_child"] = splend[-1]

    return row


if __name__ == '__main__':
    main()
