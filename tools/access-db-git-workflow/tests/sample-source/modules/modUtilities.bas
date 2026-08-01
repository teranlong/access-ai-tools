Option Compare Database
Option Explicit

' =========================================================
' modUtilities - Common utility functions
' =========================================================

Public Function FormatPhoneNumber(ByVal strPhone As String) As String
    ' Formats a 10-digit phone number as (XXX) XXX-XXXX
    strPhone = Replace(strPhone, "-", "")
    strPhone = Replace(strPhone, "(", "")
    strPhone = Replace(strPhone, ")", "")
    strPhone = Replace(strPhone, " ", "")

    If Len(strPhone) = 10 Then
        FormatPhoneNumber = "(" & Left(strPhone, 3) & ") " & _
                           Mid(strPhone, 4, 3) & "-" & Right(strPhone, 4)
    Else
        FormatPhoneNumber = strPhone
    End If
End Function

Public Function IsValidEmail(ByVal strEmail As String) As Boolean
    ' Basic email validation
    IsValidEmail = (InStr(strEmail, "@") > 1) And _
                   (InStr(InStr(strEmail, "@") + 1, strEmail, ".") > 0)
End Function

Public Function GetCurrentUser() As String
    GetCurrentUser = Environ("USERNAME")
End Function

Public Sub LogAction(ByVal strAction As String, Optional ByVal strDetails As String = "")
    ' Log user actions for audit trail
    Dim db As DAO.Database
    Dim rs As DAO.Recordset

    Set db = CurrentDb()
    Set rs = db.OpenRecordset("tblAuditLog", dbOpenDynaset)

    rs.AddNew
    rs!ActionDate = Now()
    rs!UserName = GetCurrentUser()
    rs!Action = strAction
    rs!Details = strDetails
    rs.Update

    rs.Close
    Set rs = Nothing
    Set db = Nothing
End Sub
