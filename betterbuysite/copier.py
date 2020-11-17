import sqlite3
import json

drone_orders = sqlite3.connect("../workdir/drone_db.sqlite3")
drone_cursor = drone_orders.cursor()

def createTables():
    try:
        drone_cursor.execute("SELECT * FROM drone_order")
    except (sqlite3.OperationalError):
        drone_cursor.execute("CREATE TABLE 'drone_order'('id' integer NOT NULL PRIMARY KEY AUTOINCREMENT, 'status' varchar(50) NOT NULL, 'currency' varchar(7) NOT NULL, '_subtotal' decimal NOT NULL, '_total' decimal NOT NULL, 'created_at' datetime NOT NULL, 'updated_at' datetime NOT NULL, 'extra' text NOT NULL, 'stored_request' text NOT NULL, 'number' integer unsigned NULL UNIQUE CHECK ('number' >= 0), 'shipping_address_text' text NULL, 'billing_address_text' text NULL, 'token' varchar(40) NULL, 'customer_id' integer NOT NULL REFERENCES 'betterbuysite_customer' ('user_id') DEFERRABLE INITIALLY DEFERRED, 'delivery_status' varchar(10) NOT NULL)")
    except:
        print(sys.exc_info()[0], "has occurred")

    try:
        drone_cursor.execute("SELECT * FROM drone_assignment")
    except (sqlite3.OperationalError):
        drone_cursor.execute("CREATE TABLE 'drone_assignment'('drone_id' integer NOT NULL, 'order_id' integer)")
    except:
        print(sys.exc_info()[0], "has occurred")

createTables()

site_orders = sqlite3.connect("../workdir/db.sqlite3")

site_cursor = site_orders.cursor()

site_rows = site_cursor.execute("SELECT * FROM betterbuysite_order WHERE extra LIKE '%drone-delivery%'").fetchall()
drone_rows = drone_cursor.execute("SELECT * FROM drone_order").fetchall()

def isExistingRow(site_row):
    for i in range(0,len(drone_rows)):
        if(site_row[0] == drone_rows[i][0]):
            return True
    return False

def addDeliveryStatus(site_row):
    drone_order_row = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    for i in range(0,len(site_row)):
        drone_order_row[i] = site_row[i]
    drone_order_row[14] = 'false'
    return drone_order_row

def updateDroneDb():
    for i in range(0,len(site_rows)):
        if(isExistingRow(site_rows[i])):
            continue
        drone_cursor.execute("INSERT INTO drone_order VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", addDeliveryStatus(site_rows[i]))

def droneExists(droneID, drone_assignment_rows):
    for i in range(0, len(drone_assignment_rows)):
        if(droneID == drone_assignment_rows[i][0]):
            return True
    return False

def instantiateDrones(droneAmount):
    drone_assignment_rows = drone_cursor.execute("SELECT * FROM drone_assignment").fetchall()
    for i in range(1,droneAmount + 1):
        if(droneExists(i,drone_assignment_rows)):
            continue
        drone_cursor.execute("INSERT INTO drone_assignment (drone_id) VALUES (?)", [i])

def assignOrders():
    availableDronesRows = drone_cursor.execute("SELECT * FROM drone_assignment WHERE order_id IS NULL").fetchall()
    availableOrdersRows = drone_cursor.execute("SELECT * FROM drone_order WHERE delivery_status IS 'waiting'").fetchall()
    availableDronesNum = len(availableDronesRows)
    availableOrdersNum = len(availableOrdersRows)

    for i in range(0, availableDronesNum):
        if(availableOrdersNum <= i):
            break
        drone_cursor.execute("UPDATE drone_assignment SET order_id = (?) WHERE drone_id = (?)", (availableOrdersRows[i][0], availableDronesRows[i][0]))
        drone_cursor.execute("UPDATE drone_order SET delivery_status = (?) WHERE id = (?)", ('busy', availableOrdersRows[i][0]))

def assignDroneOrders():
    droneAmount = 10
    instantiateDrones(droneAmount)
    assignOrders()

def resetDroneAssignmentTable():
    drone_cursor.execute("DELETE FROM 'drone_assignment'")
    for i in range(0, len(drone_rows)):
        drone_cursor.execute("UPDATE drone_order SET delivery_status = (?) WHERE id = (?)", ('waiting', drone_rows[i][0]))

updateDroneDb()
assignDroneOrders()
# resetDroneAssignmentTable()

drone_orders.commit()
drone_orders.close()
site_orders.close()
