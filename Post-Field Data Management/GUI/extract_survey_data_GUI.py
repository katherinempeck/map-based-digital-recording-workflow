import wx
from wx.lib.wordwrap import wordwrap
import wx.adv

from source_functions import *

#This basic structure is modified from the "Hello World 2" script in the wxPython documentation https://wxpython.org/pages/overview/
#To compile
    #pyinstaller --window --icon icons.icns extract_survey_data_GUI.py

class AppFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(AppFrame, self).__init__(*args, **kw)
        self.SetSize((750, 500))
        self.pnl = wx.Panel(self)

        self.surv_data = wx.TextCtrl(self.pnl, -1, "", wx.Point(10, 10), wx.Size(175, 25))
        addSurveyData = wx.Button(self.pnl, label = 'Select Survey Data Folder', pos = wx.Point(200, 10))
        addSurveyData.Bind(wx.EVT_BUTTON, self.onSelectSurvey)

        self.out_folder = wx.TextCtrl(self.pnl, -1, "", wx.Point(10, 40), wx.Size(175, 25))
        addOutputFolder = wx.Button(self.pnl, label = 'Select Output Folder', pos = wx.Point(200, 42))
        addOutputFolder.Bind(wx.EVT_BUTTON, self.onSelectOutput)

        #Add text box here for inputting EPSG into site form to text function
        wx.StaticText(self.pnl, label='Enter output projected coordinate system (as EPSG code)', pos = wx.Point(200, 80))
        self.epsg = wx.TextCtrl(self.pnl, -1, "", wx.Point(10, 75), wx.Size(175, 25))

        runScript = wx.Button(self.pnl, label = 'Run', pos = wx.Point(10, 150))
        runScript.Bind(wx.EVT_BUTTON, self.extractData)

        clearData = wx.Button(self.pnl, label = 'Clear', pos = wx.Point(100, 150))
        clearData.Bind(wx.EVT_BUTTON, self.onClearTxt)

        self.makeMenuBar()

        self.CreateStatusBar()
        self.SetStatusText("Add files to begin")

        #Add static text which can be updated with error messages
        self.SQLerrortext = wx.StaticText(self.pnl, label = '', pos = wx.Point(10, 200))
        self.otherPhotos = wx.StaticText(self.pnl, label = '', pos = wx.Point(10, 250))
        self.crs = wx.StaticText(self.pnl, label = '', pos = wx.Point(10, 180))

    def makeMenuBar(self):
        fileMenu = wx.Menu()
        instItem = fileMenu.Append(-1, "&Instructions\tCtrl-I", "Click for basic instructions")
        aboutItem = fileMenu.Append(-1, "&About\tCtrl-H", "Click for more info")
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT)
        helpMenu = wx.Menu()
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)
        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        self.Bind(wx.EVT_MENU, self.OnInst, instItem)

    def OnExit(self, event):
        self.Close(True)

    def OnInst(self, event):
        wx.MessageBox('1) Click "Select Survey Data Folder"\n 2) Select the folder containing the final exported GeoPackages\n 3) Click "Select Output Folder" \n 4) Select the folder into which you would like the survey data extracted \n 5) Click "Run" to extract data into the output folder \n Note: Visit the project repo (see "About") for more detailed documentation')

    def OnAbout(self, event):
        info = wx.adv.AboutDialogInfo()
        info.Name = "Extract Avenza Data"
        info.Version = "0.0.1 Beta"
        info.Copyright = "(C) 2024 NMC Cultural Resource Sciences"
        info.Description = wordwrap(
            "This app is designed to extract archaeological survey data collected using the Avenza Maps schema in the NMC Digital Recording repository. Visit the repository page for more information:",
            350, wx.ClientDC(self.pnl))
        info.SetWebSite('https://github.com/NMC-CRS', desc = 'Project GitHub Repository')
        info.Developers = ["Katherine Peck, PhD and Grant Snitker, PhD"]
        info.License = wordwrap("MIT License: \n This software is released under an MIT License. Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the 'Software'), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: \n The above copyright notice and this permission notice shall be included in all copies or substantial portions of this Software. \n THIS SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OR OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE", 
                                500, 
                                wx.ClientDC(self.pnl))
        # Show the wx.AboutBox
        wx.adv.AboutBox(info)

    def onSelectSurvey(self, event):
        dlg = wx.DirDialog(
            self, 
            message = "Choose a Folder",
            style = wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            flder = dlg.GetPath()
            flder = flder.replace('\\','/')
            print(flder)
            self.surv_data.SetValue(flder)
        dlg.Destroy()

    def onSelectOutput(self, event):
        dlg = wx.DirDialog(
            self, 
            message = "Choose a Folder",
            style = wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            flder = dlg.GetPath()
            flder = flder.replace('\\','/')
            print(flder)
            self.out_folder.SetValue(flder)
        dlg.Destroy()

    def onClearTxt(self, event):
        self.surv_data.SetValue('')
        self.out_folder.SetValue('')
        self.SetStatusText(f'Add files to begin')
        self.SQLerrortext.SetLabel('')
        self.otherPhotos.SetLabel('')
        self.crs.SetLabel('')
    
    def extractData(self, event):
        # try:
            survey_data_folder = self.surv_data.GetValue()
            extracted_data_folder = self.out_folder.GetValue()
            if self.epsg.GetValue() == '':
                self.crs.SetLabel('No output CRS provided. WGS 84 (EPSG:4326) was used')
                output_crs = '4326'
            else:
                output_crs = self.epsg.GetValue()
            n = organize_data_to_site_folders(survey_data_folder, extracted_data_folder, output_crs)
            if len(n) == 0:
                pass
            else:
                # self.SQLerrortext = wx.StaticText(self.pnl, label = f'{n}', pos = wx.Point(10, 150))
                self.SQLerrortext.SetLabel(f'The following failed to open as a GeoDataFrame and was opened as a DataFrame. Geometry will not be preserved: \n{n}')
            put_forms_in_subfolders(extracted_data_folder)
            p = extract_photos_and_logs(survey_data_folder, extracted_data_folder)
            if len(p) == 0:
                pass
            else:
                txt = '\n'.join(p)
                # self.otherPhotos = wx.StaticText(self.pnl, label = txt, pos = wx.Point(10, 200))
                self.otherPhotos.SetLabel(txt)
                site_form_to_text(extracted_data_folder, output_crs)
            self.SetStatusText(f'Process complete. Data available in {extracted_data_folder}')
        # except Exception as e:
        #     #Right now, if there's any failures, it shows the Python error in the message box
        #     print(e)
        #     wx.MessageBox(f'{e}')

if __name__ == '__main__':
    app = wx.App()
    frm = AppFrame(None, title = 'Extract Avenza Data')
    frm.Show()
    app.MainLoop()
