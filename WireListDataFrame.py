import string
import pandas as pd
import os


def main():
    inputfile = "Drahtliste_3ED00334R26-000.xlsx"

    df = WireListDataFrame()
    df.set_dataframe_from_excel(inputfile)
    tmp = df.get_dataframe(True)
    print(tmp)
    df.reorder_endpoints([("X8", "K3")])
    tmp = df.get_dataframe(True)
    print(tmp)

    # df.to_exc l("new_out",subheaders=False)

class WireListDataFrame():

    def __init__(self):
        self.df = pd.DataFrame([])
        self.sub_hdrs = []
        self.connections = [("", "")]

    def set_dataframe(self, df):
        if df.empty:
            return

        clean_df = pd.DataFrame([i for i in df.values if find_pattern(i)])
        self.df = self.add_meta(clean_df)

    def set_dataframe_from_excel(self, filename):
        raw_df = pd.read_excel(filename, sheet_name="Drahtliste")
        self.set_dataframe(raw_df.dropna(axis=1, how="all"))

    def add_meta(self, df):
        df = df.apply(define_parent_connectors, axis=1)
        try:
            groups = ["start_parent", "end_parent"]
            self.connections = []
            for start, end in df[groups].values:
                tup = (start, end)
                if tup not in self.connections:
                    self.connections.append((start, end))

        except KeyError:
            pass

        df.fillna(value="", inplace=True)
        return df.apply(add_marker, axis=1)

    def veto(self, df):
        veto = ["marker", "start_parent", "end_parent",
                "start_child", "end_child"]
        cols = [c for c in df.columns if c not in veto]

        return df[cols]

    def get_dataframe(self, sort_rows=False, subheaders=False):
        self.sub_hdrs = []

        if sort_rows and subheaders:
            export_df = self._get_grouped_dataframe()
        elif sort_rows and not subheaders:
            export_df = self._get_sorted_dataframe()
        else:
            export_df = self.df

        return self.veto(export_df)

    def find_connections(self, start, end):
        entries = []
        for idx, row in self.df.iterrows():
            if row["start_parent"] == start and row["end_parent"] == end:
                entries.append(idx)
        return entries

    def reorder_endpoints(self, new_connections=[]):
        for start, end in new_connections:
            for i, row in self.df.iterrows():
                if row["end_parent"] == start and row["start_parent"] == end:
                    self.df.loc[i] = switch_endpoints(row)
        self.df = self.add_meta(self.df)

    def _get_sorted_dataframe(self):
        self.sub_hdrs = []
        sorted_df = sort_by_connector(self.df)
        groups = ["start_parent", "end_parent"]
        self.connections = []
        for start, end in sorted_df[groups].values:
            tup = (start, end)
            if tup not in self.connections:
                self.connections.append((start, end))
        return sorted_df

    def _get_grouped_dataframe(self, sort_rows=True):

        if sort_rows:
            grouped_df = self._get_sorted_dataframe()
        else:
            grouped_df = self.df

        header = ["Konfektion_A", "von", "<", "nr.", ">", "zu",
                  "Konfektion_B", "Querschnitt", "Länge(mm)", "Draht-Type"]
        columns = {i: col for i, col in enumerate(header)}
        grouped_df = grouped_df.rename(columns=columns)

        for i, row in grouped_df.iterrows():
            sub_header = row.loc["start_parent"]
            sub_header += " nach " + row.loc["end_parent"]
            if not self.sub_hdrs:
                self.sub_hdrs.append((i + len(self.sub_hdrs), sub_header))
            elif self.sub_hdrs[-1][1] != sub_header:
                self.sub_hdrs.append((i + len(self.sub_hdrs), sub_header))

        for i, hdr in self.sub_hdrs:
            grouped_df = insert_line(grouped_df, i, hdr)
        formated_df = grouped_df.fillna(value="")

        return formated_df[header]

    def export_connections(self, outfolder):
        filepath = get_filepath(outfolder=outfolder,
                                name="connections.lst")

        columns = ["start_parent", "start_child", "end_parent", "end_child"]
        connections_df = self.df[columns]

        connections_df.to_pickle(filepath)

    def export_markers(self, outfolder=""):
        with open("message_template.xml", "r") as FSO:
            message = string.Template(FSO.read())

        for i, marker in enumerate(self.df["marker"]):

            content = message.substitute(info=marker)

            filepath = get_filepath(outfolder=outfolder,
                                    name="{0}.Message.xml".format(i + 100))
            with open(filepath, "w") as FSO:
                FSO.write(content)

    def to_excel(self, filename, outfolder=""):

        if self.df.empty:
            return

        raw_df = self.get_dataframe()
        grouped_df = self.get_dataframe(sort_rows=True, subheaders=True)

        filepath = get_filepath(outfolder=outfolder,
                                name="Drahtliste_{0}.xlsx".format(filename))

        writer = pd.ExcelWriter(filepath,
                                engine='xlsxwriter')

        raw_df.to_excel(writer, sheet_name='Rohdaten',
                        startrow=1, index=False)

        grouped_df.to_excel(writer, sheet_name='Drahtliste',
                            startrow=1, index=False)

        workbook = writer.book
        worksheet = writer.sheets['Drahtliste']
        cell_format = workbook.add_format()
        cell_format.set_left(1)
        cell_format.set_right(1)

        for i, width in enumerate(self.get_column_widths(grouped_df)):
            worksheet.set_column(i, i, width, cell_format)

        use_format = {'bold': 1, 'border': 6, 'align': 'center'}
        top_format = workbook.add_format(use_format)
        top_format.set_font_size(20)
        merge_format = workbook.add_format(use_format)

        worksheet.merge_range('A1:J1', filename, top_format)
        for i, sub_header in self.sub_hdrs:
            worksheet.merge_range(i + 2, 0, i + 2, len(grouped_df.columns) - 1,
                                  sub_header, merge_format)

        writer.save()

    def get_column_widths(self, df):
        header = df.columns

        for col, name in enumerate(header):
            col_width = len(str(name))
            individuals = df[name].value_counts().to_dict().keys()
            for i in individuals:
                if len(str(i)) > col_width:
                    col_width = len(str(i))
            yield col_width + 1


def get_filepath(outfolder, name):
    filepath = name
    if outfolder:
        filepath = os.path.join(outfolder, name)

    return filepath


def sort_by_connector(df):

    modified_df = df
    if not all([i in df.columns for i in ["start_parent", "end_parent"]]):
        modified_df = df.apply(define_parent_connectors, axis=1)

    # Values sorted by occurrence of start parent
    start_parents = modified_df["start_parent"].value_counts().to_dict()

    index = []
    for sp in start_parents.keys():
        sel_df = modified_df[modified_df["start_parent"] == sp]
        index += sort_by_freq(sel_df, "end_parent").index.to_list()

    return modified_df.reindex(index).reset_index(drop=True)


def sort_by_freq(df, key):
    sp_count = df[key].value_counts().to_dict()
    df = df.assign(freq=df.apply(lambda x: sp_count[x[key]], axis=1))
    df = df.sort_values(by=['freq', key], ascending=[False, True])
    return df.drop("freq", axis=1)


def find_header(df):
    rows = df.values

    for i, row in enumerate(rows):
        if all([label in row for label in ["von", "nr.", "zu"]]):
            return list(rows[i])
    return None


def switch_endpoints(row):
    row.at[1], row.at[5] = row.at[5], row.at[1]
    row.at[0], row.at[6] = row.at[6], row.at[0]

    return row


def insert_line(df, index, string):
    line = pd.DataFrame(columns=df.columns, index=[index])
    line[df.columns[0]] = string
    new_df = pd.concat([df.iloc[:index], line, df.iloc[index:]])
    return new_df.reset_index(drop=True)


def find_pattern(row):
    for i, element in enumerate(row):
        if element == "<" and row[i + 2] == ">":
            return (i - 1, i + 1, i + 3)

    symbols = [".", "X", "K", "S"]
    for i, element in enumerate(row):
        possible_start = any([sym in str(element) for sym in symbols])
        match_center = False
        match_end = False
        if possible_start:

            try:
                match_center = row[i + 2] != ""
                match_end = any([sym in str(row[i + 4]) for sym in symbols])
            except IndexError:
                continue

            found_one_dot = "." in str(element) + str(row[i + 4])

            if all([possible_start, match_center, match_end, found_one_dot]):
                return (i, i + 2, i + 4)
    return ()


def add_marker(row):
    mpos = find_pattern(row)
    if mpos:
        row["marker"] = row[mpos[0]] + "<" + row[mpos[1]] + ">" + row[mpos[2]]
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
