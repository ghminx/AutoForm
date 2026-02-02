import win32com.client as win32
import zipfile
import os
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta


# 한글 프로세스 생성
def hwp_open(frame_path=None, view=False):
    # hwp = win32.Dispatch("hwpframe.hwpobject")
    hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
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
    try:
        # 문서의 처음으로 이동
        hwp.HAction.Run("MoveTopLevelBegin")
        
        # 표로 이동(Alt + G, 조판부호(표))
        hwp.HAction.GetDefault("Goto", hwp.HParameterSet.HGotoE.HSet)
        hwp.HParameterSet.HGotoE.HSet.SetItem("DialogResult", 55)
        hwp.HParameterSet.HGotoE.SetSelectionIndex = 5
        result = hwp.HAction.Execute("Goto", hwp.HParameterSet.HGotoE.HSet)

        if result:
            hwp.HAction.Run("MoveRight")
            hwp.HAction.Run("TableCellBlock")
            return True
        else:
            return False
        
    except Exception as e:
        print(f"표로 이동 중 오류 발생: {e}")
        return False


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


def count_tables(hwp):
    hwp.HAction.Run("MoveTopLevelBegin")

    cnt = 0
    try:
        ctrl = hwp.HeadCtrl
    except Exception:
        ctrl = None

    visited = set()
    while ctrl:
        try:
            ctrl_id = getattr(ctrl, "CtrlID", None)
            # print(f"[DEBUG] CtrlID={ctrl_id}, id={id(ctrl)}")

            if ctrl_id == "tbl":
                cnt += 1

            # 무한루프 방지
            if id(ctrl) in visited:
                # print(f"[STOP] 이미 방문한 컨트롤 id={id(ctrl)} — 루프 종료")
                break
            visited.add(id(ctrl))

            # 다음 컨트롤로 이동
            ctrl = getattr(ctrl, "Next", None)
        except Exception as e:
            print(f"[ERROR] {e}")
            break

    # print(f"[RESULT] 총 표 개수: {cnt}")
    # print(f"[VISITED] {len(visited)}개 컨트롤 방문함")
    return cnt


def table_extract(hwp):
    table_dict = {}

    while True:

        current_pos = hwp.KeyIndicator()[-1][1:].split(")")[0]
        get_text(hwp)
        
        
        table_dict[current_pos] = get_text(hwp)
        
        hwp.HAction.Run("TableRightCell")
        
        next_pos = hwp.KeyIndicator()[-1][1:].split(")")[0]
        
        if current_pos == next_pos:
            break
        
    return table_dict