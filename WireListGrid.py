import wx.grid
import wx
import pandas as pd
import numpy as np
# from WireListDataFrame import WireListDataFrame

# Initial code from https://stackoverflow.com/questions/28509629
# by user "Sinan Çetinkaya"


class WireListGrid(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, wx.ID_ANY,
                              wx.DefaultPosition, wx.DefaultSize, 0)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGING, self.on_change)
        self.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.on_label_rclick)
        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_cell_rclick)
        self.selected_rows = []
        self.selected_cols = []
        self.history = []
        self.CreateGrid(100, 15)
        self.set_header()
        self.AutoSizeColumns()
        self.AutoSizeRows()

    def set_header(self):
        header = ["Konfektion_A", "von", "<", "nr.", ">", "zu",
                  "Konfektion_B", "Querschnitt", "Länge(mm)", "Draht-Type"]

        for idx, cell in enumerate(header):
            self.SetColLabelValue(idx, cell)

        for idx in range(len(header), self.GetNumberCols()):
            self.SetColLabelValue(idx, "")

    def get_col_headers(self):
        return [self.GetColLabelValue(col)
                for col in range(self.GetNumberCols())]

    def get_table(self):
        for row in range(self.GetNumberRows()):
            result = {}
            for col in range(self.GetNumberCols()):
                result[str(col)] = self.GetCellValue(row, col)
            yield result

    def get_dataframe(self):
        table = []
        for row in self.get_table():
            table.append(row)
        df = pd.DataFrame(table)

        df.replace('', np.nan, inplace=True)
        # df.dropna(axis=1, how="all", inplace=True)
        df.dropna(axis=0, how="all", inplace=True)

        return df

    def from_df(self, df, sub_headers=[]):
        if df.empty:
            return

        data = []
        for i, row in df.iterrows():
            data.append("\t".join([str(s) for s in row.to_list()]))
        data = "\n".join(data)

        text_data_object = wx.TextDataObject()
        text_data_object.SetText(data)

        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(text_data_object)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Can't open the clipboard", "Warning")
        self.SelectAll()
        self.ForceRefresh()
        self.paste(None)
        for row, sh in sub_headers:
            self.SetCellFont(row, 0, wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.SetCellValue(row, 0, sh)
            self.SetCellAlignment(row, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.SetCellSize(row, 0, 1, 10)

    def add_rows(self, event):
        for row in self.selected_rows:
            self.InsertRows(row)
        self.add_history({"type": "add_rows", "rows": self.selected_rows})

    def delete_rows(self, event):
        self.cut(event)
        rows = []
        for row in reversed(self.selected_rows):
            rows.append((
                row,
                {  # More attributes can be added
                    "label": self.GetRowLabelValue(row),
                    "size": self.GetRowSize(row)
                }
            ))
            self.DeleteRows(row)
        self.add_history({"type": "delete_rows", "rows": rows})

    def add_cols(self, event):
        for col in self.selected_cols:
            self.InsertCols(col)
        self.add_history({"type": "add_cols", "cols": self.selected_cols})
        self.set_header()
        self.AutoSizeColumns()

    def delete_cols(self, event):
        self.delete(event)
        cols = []
        for col in reversed(self.selected_cols):
            cols.append((
                col,
                {  # More attributes can be added
                    "label": self.GetColLabelValue(col),
                    "size": self.GetColSize(col)
                }
            ))
            self.DeleteCols(col)
        self.add_history({"type": "delete_cols", "cols": cols})
        self.set_header()
        self.AutoSizeColumns()

    def on_cell_rclick(self, event):
        menus = [(wx.NewIdRef(count=1), "Ausschneiden", self.cut),
                 (wx.NewIdRef(count=1), "Kopieren", self.copy),
                 (wx.NewIdRef(count=1), "Einfügen", self.paste)]
        popup_menu = wx.Menu()
        for menu in menus:
            if menu is None:
                popup_menu.AppendSeparator()
                continue
            popup_menu.Append(menu[0], menu[1])
            self.Bind(wx.EVT_MENU, menu[2], id=menu[0])

        self.PopupMenu(popup_menu, event.GetPosition())
        popup_menu.Destroy()
        return

    def on_label_rclick(self, event):
        menus = [(wx.NewIdRef(count=1), "Ausschneiden", self.cut),
                 (wx.NewIdRef(count=1), "Kopieren", self.copy),
                 (wx.NewIdRef(count=1), "Einfügen", self.paste),
                 None]

        # Select if right clicked row or column is not in selection
        if event.GetRow() > -1:
            if not self.IsInSelection(row=event.GetRow(), col=1):
                self.SelectRow(event.GetRow())
            self.selected_rows = self.GetSelectedRows()

            menus += [(wx.NewIdRef(count=1), "Reihe hinzufügen",
                       self.add_rows)]
            menus += [(wx.NewIdRef(count=1), "Reihe löschen",
                       self.delete_rows)]
        elif event.GetCol() > -1:
            if not self.IsInSelection(row=1, col=event.GetCol()):
                self.SelectCol(event.GetCol())
            self.selected_cols = self.GetSelectedCols()

            menus += [(wx.NewIdRef(count=1), "Spalte hinzufügen",
                       self.add_cols)]
            menus += [(wx.NewIdRef(count=1), "Spalte löschen",
                       self.delete_cols)]
        else:
            return

        popup_menu = wx.Menu()
        for menu in menus:
            if menu is None:
                popup_menu.AppendSeparator()
                continue
            popup_menu.Append(menu[0], menu[1])
            self.Bind(wx.EVT_MENU, menu[2], id=menu[0])

        self.PopupMenu(popup_menu, event.GetPosition())
        popup_menu.Destroy()
        return

    def on_change(self, event):
        cell = event.GetEventObject()
        row = cell.GetGridCursorRow()
        col = cell.GetGridCursorCol()
        attribute = {"value": self.GetCellValue(row, col)}
        self.add_history({"type": "change", "cells": [(row, col, attribute)]})
        self.AutoSizeColumns()
        self.AutoSizeRows()

    def add_history(self, change):
        self.history.append(change)

    def undo(self):
        if not len(self.history):
            return

        action = self.history.pop()
        if action["type"] == "change" or action["type"] == "delete":
            for row, col, attribute in action["cells"]:
                self.SetCellValue(row, col, attribute["value"])
                if action["type"] == "delete":
                    self.SetCellAlignment(row, col, *attribute["alignment"])

        elif action["type"] == "delete_rows":
            for row, attribute in reversed(action["rows"]):
                self.InsertRows(row)
                self.SetRowLabelValue(row, attribute["label"])
                self.SetRowSize(row, attribute["size"])

        elif action["type"] == "delete_cols":
            for col, attribute in reversed(action["cols"]):
                self.InsertCols(col)
                self.SetColLabelValue(col, attribute["label"])
                self.SetColSize(col, attribute["size"])

        elif action["type"] == "add_rows":
            for row in reversed(action["rows"]):
                self.DeleteRows(row)

        elif action["type"] == "add_cols":
            for col in reversed(action["cols"]):
                self.DeleteCols(col)
        else:
            return

        self.set_header()
        self.AutoSizeColumns()

    def on_key(self, event):
        """
        Handles all key events.
        """
        # print(event.GetKeyCode())
        # Ctrl+C or Ctrl+Insert
        if event.ControlDown() and event.GetKeyCode() in [67, 322]:
            self.copy(event)

        # Ctrl+V
        elif event.ControlDown() and event.GetKeyCode() == 86:
            self.paste(event)

        # DEL
        elif event.GetKeyCode() in [8, 46]:
            self.delete(event)

        # Ctrl+A
        elif event.ControlDown() and event.GetKeyCode() == 65:
            self.SelectAll()

        # Ctrl+Z
        elif event.ControlDown() and event.GetKeyCode() == 90:
            self.undo()

        # Ctrl+X
        elif event.ControlDown() and event.GetKeyCode() == 88:
            # Call delete method
            self.cut(event)

        # Ctrl+V or Shift + Insert
        elif (event.ControlDown() and event.GetKeyCode() == 67) \
                or (event.ShiftDown() and event.GetKeyCode() == 322):
            self.paste(event)

        else:
            event.Skip()

    def get_selection(self):
        """
        Returns selected range's start_row, start_col, end_row, end_col
        If there is no selection, returns selected cell's
        start_row=end_row, start_col=end_col
        """
        if not len(self.GetSelectionBlockTopLeft()):
            selected_columns = self.GetSelectedCols()
            selected_rows = self.GetSelectedRows()
            if selected_columns:
                start_col = selected_columns[0]
                end_col = selected_columns[-1]
                start_row = 0
                end_row = self.GetNumberRows() - 1
            elif selected_rows:
                start_row = selected_rows[0]
                end_row = selected_rows[-1]
                start_col = 0
                end_col = self.GetNumberCols() - 1
            else:
                start_row = end_row = self.GetGridCursorRow()
                start_col = end_col = self.GetGridCursorCol()
        elif len(self.GetSelectionBlockTopLeft()) > 1:
            wx.MessageBox("Multiple selections are not supported", "Warning")
            return []
        else:
            start_row, start_col = self.GetSelectionBlockTopLeft()[0]
            end_row, end_col = self.GetSelectionBlockBottomRight()[0]

        return [start_row, start_col, end_row, end_col]

    def get_selected_cells(self):
        # returns a list of selected cells
        selection = self.get_selection()
        if not selection:
            return

        start_row, start_col, end_row, end_col = selection
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                yield [row, col]

    def copy(self, event):
        """
        Copies range of selected cells to clipboard.
        """

        selection = self.get_selection()
        if not selection:
            return []
        start_row, start_col, end_row, end_col = selection

        data = u''

        rows = range(start_row, end_row + 1)
        for row in rows:
            columns = range(start_col, end_col + 1)
            for idx, column in enumerate(columns, 1):
                if idx == len(columns):
                    # if we are at the last cell of the row,
                    # add new line instead
                    data += self.GetCellValue(row, column) + "\n"
                else:
                    data += self.GetCellValue(row, column) + "\t"

        text_data_object = wx.TextDataObject()
        text_data_object.SetText(data)

        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(text_data_object)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Can't open the clipboard", "Warning")

    def paste(self, event):
        if not wx.TheClipboard.Open():
            wx.MessageBox("Can't open the clipboard", "Warning")
            return False

        clipboard = wx.TextDataObject()
        wx.TheClipboard.GetData(clipboard)
        data = clipboard.GetText()
        wx.TheClipboard.Close()

        if data[-1] == "\n":
            data = data[:-1]

        try:
            cells = self.get_selected_cells()
            cell = next(cells)
        except StopIteration:
            return False

        start_row = end_row = cell[0]
        start_col = end_col = cell[1]
        max_row = self.GetNumberRows()
        max_col = self.GetNumberCols()

        history = []
        out_of_range = False

        for row, line in enumerate(data.splitlines()):
            target_row = start_row + row
            if not (0 <= target_row < max_row):
                out_of_range = True
                break

            if target_row > end_row:
                end_row = target_row

            for col, value in enumerate(line.split("\t")):
                target_col = start_col + col
                if not (0 <= target_col < max_col):
                    out_of_range = True
                    break

                if target_col > end_col:
                    end_col = target_col

                # save previous value of the cell for undo
                old_value = self.GetCellValue(target_row, target_col)
                history.append([target_row, target_col, {"value": old_value}])

                self.SetCellValue(target_row, target_col, value)

        self.SelectBlock(start_row, start_col, end_row, end_col)
        if out_of_range:
            wx.MessageBox("Pasted data is out of Grid range", "Warning")

        self.add_history({"type": "change", "cells": history})
        self.AutoSizeColumns()
        self.AutoSizeRows()

    def delete(self, event):
        cells = []
        for row, col in self.get_selected_cells():
            attributes = {
                "value": self.GetCellValue(row, col),
                "alignment": self.GetCellAlignment(row, col)
            }
            cells.append((row, col, attributes))
            self.SetCellValue(row, col, "")

        self.add_history({"type": "delete", "cells": cells})
        self.AutoSizeColumns()
        self.AutoSizeRows()

    def cut(self, event):
        self.copy(event)
        self.delete(event)


if __name__ == '__main__':
    class MyFrame(wx.Frame):
        def __init__(self, parent, ID, title, pos=wx.DefaultPosition,
                     size=wx.Size(800, 400), style=wx.DEFAULT_FRAME_STYLE):
            wx.Frame.__init__(self, parent, ID, title, pos, size, style)
            # agrid = WireListGrid(self)
            # wireFrame = WireListDataFrame()
            # wireFrame.set_dataframe_from_excel("Drahtliste_3ED00334R26-000.xlsx")
            # agrid.from_df( wireFrame.get_sorted_dataframe(),
            #                sub_headers = wireFrame.sub_headers )

    class MyApp(wx.App):
        def OnInit(self):
            frame = MyFrame(None, -1, "A copy and paste grid")
            frame.Show(True)
            self.SetTopWindow(frame)
            return True

    app = MyApp()
    app.MainLoop()
