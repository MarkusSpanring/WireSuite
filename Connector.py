import wx
import wx.lib.mixins.listctrl
import numpy as np


class ConnectorList(wx.ListCtrl,
                wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin,
                wx.lib.mixins.listctrl.TextEditMixin,
                wx.lib.mixins.listctrl.ListRowHighlighter):

    def __init__(self, parent, *args, **kw):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=wx.LC_REPORT)
        wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__(self)
        wx.lib.mixins.listctrl.TextEditMixin.__init__(self)
        wx.lib.mixins.listctrl.ListRowHighlighter.__init__(self)

    def getFullListData(self):

        rows = self.GetItemCount()
        cols = self.GetColumnCount()
        data = np.empty( (rows,cols),dtype=object )

        for row in range(rows):
            for col in range(cols):
                item = self.GetItem(itemIdx=row, col=col)
                data[row,col] = item.GetText()
        return data
    def setFullListData(self,data):
        self.DeleteAllItems()
        rows,cols = data.shape

        for i in range(rows):
            index = self.InsertItem(i, data[i,0] )
            self.SetItem(index, 1, data[i,1] )


class ConnectorData():

    def __init__(self,name="",nPins=0,data=[]):
        self.name = name
        self.nPins = nPins
        self.data = data

    def getUsedPins(self):
        return self.data[:,1]

    def packData(self):
        
        connections = {}
        for item in self.data:
            connections[item[0]] = item[1]

        packedData = {self.name:{"nPins":self.nPins, "connections": connections} }
        return packedData

    def unpackData(self, name, packedData):
        self.name = name
        self.nPins = packedData["nPins"]

        rows = len(packedData["connections"])
        connections = packedData["connections"]
        data = np.empty( (rows,2),dtype=object )

        for i, pin in enumerate(connections):
            data[i,0] = pin
            data[i,1] = connections[pin]
        self.data = data



class ConnectorEditorDialog(wx.Dialog):

    def __init__(self, parent, name = "", forbiddenPins=[], nPins = 0, maxPins=37, data=[]):
        super(ConnectorEditorDialog, self).__init__(parent, title='Neuer Stecker')

        self.maxPins = maxPins - len(forbiddenPins)
        self.forbiddenPins =  forbiddenPins
        self.availablePins = [str(i) for i in range(1,maxPins+1) if not str(i) in self.forbiddenPins]
        self.dataContainer = ConnectorData(name=name,nPins = nPins,  data=data)

        self.InitUI()
        self.Centre()

    def InitUI(self):

        self.panel = wx.Panel(self)
        self.ToggleWindowStyle(wx.STAY_ON_TOP)

        vbox = wx.BoxSizer(wx.VERTICAL)

        inputBox = wx.BoxSizer(wx.HORIZONTAL)
        stStkBez = wx.StaticText(self.panel, label='Steckerbezeichnung')
        inputBox.Add(stStkBez, flag=wx.RIGHT|wx.CENTER, border=8)
        self.tcStkBez = wx.TextCtrl(self.panel, value=self.dataContainer.name)
        inputBox.Add(self.tcStkBez, proportion=1)

        stKontakte = wx.StaticText(self.panel, label='Kontakte')
        inputBox.Add(stKontakte, flag=wx.LEFT|wx.CENTER, border=8)
        self.scKontakte = wx.SpinCtrl(self.panel, value=str(self.dataContainer.nPins), min=1, max=self.maxPins)
        inputBox.Add(self.scKontakte, 1)
        vbox.Add(inputBox, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        self.connectorList = ConnectorList(self.panel)
        self.connectorList.InsertColumn(0, 'Steckerkontakt', width=150)
        self.connectorList.InsertColumn(1, 'Interner Kontakt', width=150)
        if len(self.dataContainer.data) > 0:
            self.connectorList.setFullListData(self.dataContainer.data)

        hbox3.Add(self.connectorList, proportion=1, flag=wx.EXPAND, border=10)
        vbox.Add(hbox3, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)

        self.connectorList.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.userModifyList)

        hboxButton = wx.BoxSizer(wx.HORIZONTAL)
        self.btnSave = wx.Button(self.panel, label='Speichern', size=(80, 30))
        self.btnSave.Disable()
        hboxButton.Add(self.btnSave)
        vbox.Add(hboxButton, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=10)


        self.tcStkBez.Bind(wx.EVT_TEXT, self.generateListBox)
        self.scKontakte.Bind(wx.EVT_SPINCTRL, self.generateListBox)
        self.btnSave.Bind(wx.EVT_BUTTON, self.onSaveClicked)

        # self.btnSave.Bind(wx.EVT_BUTTON, self.fillDataContainer)

        self.panel.SetSizer(vbox)


    def onSaveClicked(self, event):
        self.Close()

    def generateListBox(self,e):

        name = self.tcStkBez.GetValue()
        nPins = self.scKontakte.GetValue()
        data = np.empty( (nPins,2),dtype=object )

        for i in range(nPins):
            item = ".".join([name, str(i+1) ])
            data[i,0]=item
            data[i,1]=self.availablePins[i]

        self.connectorList.setFullListData(data)
        self.fillDataContainer()
        if nPins > 0 and name:
            self.btnSave.Enable()

    def userModifyList(self,e):

        data = self.connectorList.getFullListData()

        row_id = e.GetIndex() #Get the current row
        col_id = e.GetColumn () #Get the current column
        old_data = data[row_id,col_id]
        new_data = e.GetLabel() #Get the changed data
        data[row_id,col_id] = new_data

        self.connectorList.setFullListData(data)
        self.fillDataContainer()

    def fillDataContainer(self):
        self.dataContainer.name = self.tcStkBez.GetValue()
        self.dataContainer.nPins = self.scKontakte.GetValue()
        self.dataContainer.data = self.connectorList.getFullListData()

def main():

    app = wx.App()
    ex = ConnectorGUI(None, forbiddenPins=[2,5,6], maxPins=37)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()