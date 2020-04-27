import wx
import wx.lib.mixins.listctrl
import json
import os
import time
from ConnectorDialog import ConnectorEditorDialog, Connector


class AutoWidthListCtrl(wx.ListCtrl,
                        wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin,
                        wx.lib.mixins.listctrl.ListRowHighlighter):

    def __init__(self, parent, *args, **kw):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=wx.LC_REPORT)
        wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__(self)
        wx.lib.mixins.listctrl.ListRowHighlighter.__init__(self)

class AdapterEditorDialog(wx.Frame):

    def __init__(self, parent=None, adptFile = "", *args, **kw):
        super(AdapterEditorDialog, self).__init__( parent,size=(400,300),*args, **kw)
        self.directory = parent.directory
        self.InitUI()
        self.ConEditor = None
        self.ConIdx = 0
        self.ConList = []
        if adptFile:
            self.loadAdptFile(adptFile)

    def InitUI(self):

        panel = wx.Panel(self)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.listbox = AutoWidthListCtrl(panel)
        self.listbox.InsertColumn(0, 'Stecker',width=100)
        self.listbox.InsertColumn(1, 'Info')
        self.listbox.Bind(wx.EVT_LIST_ITEM_SELECTED, lambda e, tmp="sel": self.OnItemFocus(e,tmp) )
        self.listbox.Bind(wx.EVT_LIST_ITEM_DESELECTED, lambda e, tmp="dsel": self.OnItemFocus(e,tmp))

        hbox.Add(self.listbox, wx.ID_ANY, wx.EXPAND | wx.ALL, 7)

        btnPanel = wx.Panel(panel)
        vbox = wx.BoxSizer(wx.VERTICAL)

        stStkBez = wx.StaticText(btnPanel, label='Adaptername:')
        self.tcAdptName = wx.TextCtrl(btnPanel, wx.ID_ANY,
                                      value=time.strftime("%Y-%m-%d_%H%M", time.localtime()),
                                      size=(150, 22))

        self.newBtn = wx.Button(btnPanel, wx.ID_ANY, 'Neuer Stecker', size=(150, 30))
        self.ediBtn = wx.Button(btnPanel, wx.ID_ANY, 'Stecker bearbeiten', size=(150, 30))
        self.delBtn = wx.Button(btnPanel, wx.ID_ANY, 'Stecker löschen', size=(150, 30))
        self.saveBtn = wx.Button(btnPanel, wx.ID_ANY, 'Adapter speichern', size=(150, 30))
        self.ediBtn.Disable()
        self.delBtn.Disable()
        self.saveBtn.Disable()

        self.Bind(wx.EVT_BUTTON, self.OnNewConnectorClicked, self.newBtn)
        self.Bind(wx.EVT_BUTTON, self.OnEditConnectorClicked, self.ediBtn)
        self.Bind(wx.EVT_BUTTON, self.OnDeleteConnectorClicked, self.delBtn)
        self.Bind(wx.EVT_BUTTON, self.OnSaveClicked, self.saveBtn)
        self.Bind(wx.EVT_TEXT, self.OnAdapterNameChanged, self.tcAdptName)

        vbox.Add((-1, 7))
        vbox.Add(stStkBez)
        vbox.Add(self.tcAdptName,0,wx.TOP)
        vbox.Add((-1, 20))
        vbox.Add(self.newBtn, 0, wx.TOP)
        vbox.Add(self.ediBtn, 0, wx.TOP)
        vbox.Add(self.delBtn, 0, wx.TOP)
        vbox.Add((-1, 40))
        vbox.Add(self.saveBtn, 0, wx.BOTTOM)

        btnPanel.SetSizer(vbox)
        hbox.Add(btnPanel, 0.6, wx.EXPAND | wx.RIGHT , 10)

        panel.SetSizer(hbox)

        self.SetTitle('Neuer Adapter')
        self.Centre()

    def loadAdptFile(self, adptFile):
        filepath = "{adapter}/{file}.adt".format(file=adptFile,**self.directory)
        with open(filepath, "r") as FSO:
            setting = json.load(FSO)
        os.remove(filepath)

        for con, data in setting.items():
            tmp = Connector()
            tmp.unpackData(name=con, packedData=data)
            self.ConList.append(tmp)

        for i, con in enumerate(self.ConList):
            index = self.listbox.InsertItem(i, con.name )
            self.listbox.SetItem(index, 1, str(con.nPins)+" pol." )
        self.tcAdptName.SetValue(adptFile)
        self.saveBtn.Enable()

    def getUsedPins(self):
        usedPins = []

        for container in self.ConList:
            usedPins += list(container.getUsedPins())

        usedPins = list(set([i for i in usedPins]))
        return usedPins

    def OnAdapterNameChanged(self, e):
        if len(self.ConList) > 0 and self.tcAdptName.GetValue():
            self.saveBtn.Enable()
        else:
            self.saveBtn.Disable()

    def OnItemFocus(self,e,i):
        if i == "sel":
            self.ediBtn.Enable()
            self.delBtn.Enable()
        elif i == "dsel":
            self.ediBtn.Disable()
            self.delBtn.Disable()

    def OnSaveClicked(self, e):
        packedData = {}
        for con in self.ConList:

            if not con.name in packedData:
                packedData.update(con.packData())
            else:
                wx.MessageBox('Duplikat gefunden.\nSteckername "{0}" ist bereits vergeben!'.format(con.name),
                              'Info', wx.OK | wx.ICON_WARNING)
                return

        with open("{adapter}/{0}.adt".format(self.tcAdptName.GetValue(),**self.directory),"w") as FSO:
            json.dump(packedData, FSO, indent = 2)

        self.Close()


    def OnNewConnectorClicked(self, e):

        if not self.ConEditor:
            self.ConEditor = ConnectorEditorDialog(self,forbiddenPins=self.getUsedPins())
            self.ConEditor.Bind(wx.EVT_CLOSE, self.OnConnectorEditorClosed)
            self.ConIdx = self.listbox.GetItemCount()
            self.ConEditor.Show()


    def OnEditConnectorClicked(self, e):

        if not self.ConEditor:
            self.ConIdx = self.listbox.GetFocusedItem()
            forbiddenPins = [i for i in self.getUsedPins() if i not in self.ConList[self.ConIdx].getUsedPins()]

            self.ConEditor = ConnectorEditorDialog(self, name = self.ConList[self.ConIdx].name,
                                                   nPins= self.ConList[self.ConIdx].nPins,
                                                   data = self.ConList[self.ConIdx].data,
                                                   forbiddenPins=forbiddenPins)

            self.ConEditor.Bind(wx.EVT_CLOSE, self.OnConnectorEditorClosed)
            self.ConEditor.Show()

    def OnDeleteConnectorClicked(self, e):
        if not self.ConEditor:
            self.ConIdx = self.listbox.GetFocusedItem()
            self.listbox.DeleteItem(self.ConIdx )
            self.ConList.pop(self.ConIdx)
        if len(self.ConList) == 0:
            self.ediBtn.Disable()
            self.delBtn.Disable()
            self.saveBtn.Disable()

    def OnConnectorEditorClosed(self, e):
        if not self.ConEditor.Connector.valid:
            e.Skip()
            return

        if self.ConIdx < len(self.ConList):
            self.ConList[self.ConIdx] = self.ConEditor.Connector
            self.listbox.DeleteItem(self.ConIdx )
        else:
            self.ConList.append(self.ConEditor.Connector)

        index = self.listbox.InsertItem(self.ConIdx, self.ConEditor.Connector.name )
        self.listbox.SetItem(index, 1, str(self.ConEditor.Connector.nPins)+" pol." )

        if len(self.ConList) > 0 and self.tcAdptName.GetValue():
            self.saveBtn.Enable()

        e.Skip()


def main():

    app = wx.App()
    ex = AdapterEditorDialog(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()