import win32com.client as win32
import zipfile
import os
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta


# 한글 프로세스 생성
def hwp_open(frame_path=None, view=False):
    hwp = win32.DispatchEx("hwpframe.hwpobject")
    hwp.XHwpWindows.Item(0).Visible = view
    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
    hwp.RegisterModule("Clipboard", "")  
    
    # frame_path가 있을 때만 Open 호출
    if frame_path is not None:
        hwp.Open(frame_path)
    else:
        # 새 문서 생성
        hwp.HAction.Run("FileNew")
    
    return hwp

#  표 내부로 이동 
def move_to_table(hwp):
    hwp.HAction.GetDefault("Goto", hwp.HParameterSet.HGotoE.HSet)
    hwp.HParameterSet.HGotoE.HSet.SetItem("DialogResult", 55)
    hwp.HParameterSet.HGotoE.SetSelectionIndex = 5
    hwp.HAction.Execute("Goto", hwp.HParameterSet.HGotoE.HSet)
    hwp.HAction.Run("MoveRight")


    hwp.HAction.Run("TableCellBlock")


def move_to_cell(hwp, cell):

    # A1 셀로 이동
    hwp.Run("CloseEx")
    hwp.FindCtrl()
    hwp.Run("ShapeObjTableSelCell")

    # 목표셀로 이동
    while True:
        current_pos = hwp.KeyIndicator()[-1][1:].split(")")[0]

        if current_pos != cell:
            hwp.HAction.Run("TableRightCell")
            
        else:
            hwp.HAction.Run("TableCellBlock")
            break
        
        
# 현태 선택중인 셀의 텍스트를 가져오는 함수
def get_text(hwp):
    hwp.InitScan(Range=0xff)
    _, text = hwp.GetText()
    hwp.ReleaseScan()
    return text