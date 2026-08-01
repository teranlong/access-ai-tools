SELECT tblOrders.OrderID, tblOrders.OrderDate, tblCustomers.CustomerName, tblOrders.TotalAmount, tblOrders.Status
FROM tblOrders INNER JOIN tblCustomers ON tblOrders.CustomerID = tblCustomers.CustomerID
WHERE tblOrders.Status = "Open"
ORDER BY tblOrders.OrderDate DESC;
