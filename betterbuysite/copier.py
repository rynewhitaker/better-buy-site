import sqlite3
import json

drone_orders = sqlite3.connect("workdir/drone_db.sqlite3")
drone_cursor = drone_orders.cursor() #Cursor used to run sql in drone orders db

def createTables(): #Checks to see if all tables are created, if not created it creates them
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

site_orders = sqlite3.connect("workdir/db.sqlite3")
site_cursor = site_orders.cursor() #Cursor used to run sql in site order db

site_rows = site_cursor.execute("SELECT * FROM betterbuysite_order WHERE extra LIKE '%drone-delivery%'").fetchall() #gives site_rows all order rows in betterbuysite_order that are drone deliverable
drone_rows = drone_cursor.execute("SELECT * FROM drone_order").fetchall() #gives drone_rows all order rows in drone_order
drone_assignment_rows = drone_cursor.execute("SELECT * FROM drone_assignment").fetchall() #gives drone_assignment_rows all rows in drone_assignments

def addDroneOrderRow(newDroneRow): #Inserts submitted information into a new row of the drone_order table in drone_db
    drone_cursor.execute("INSERT INTO drone_order VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", newDroneRow)

def changeDroneDeliveryStatus(drone_order_id, newStatus): #changes the delivery status to a given order in drone order #newStatus should only be 'waiting', 'busy', and 'delivered'
    drone_cursor.execute("UPDATE drone_order SET delivery_status = (?) WHERE id = (?)", (newStatus, drone_order_id))

def assignDrone(drone_id, order_id): #Assigns a given drone to a given order in the drone assignment table
    drone_cursor.execute("UPDATE drone_assignment SET order_id = (?) WHERE drone_id = (?)", (order_id, drone_id))

def unassignDrone(drone_id): #Removes in assigned order to a given drone in the drone assignment table
    drone_cursor.execute("UPDATE drone_assignment SET order_id = NULL WHERE drone_id = (?)", [drone_id])

def getAssignedDroneRows(): #returns all of the rows in drone assignment where a drone is assigned an order
    assignedDrones = drone_cursor.execute("SELECT * FROM drone_assignment WHERE order_id IS NOT NULL").fetchall()
    return assignedDrones

def getUnassignedDroneRows(): #returns all of the rows in drone assignment where a drone does not have an order
    unassignedDrones = drone_cursor.execute("SELECT * FROM drone_assignment WHERE order_id IS NULL").fetchall()
    return unassignedDrones

def getAssignedDroneOrder(drone_id): #returns the order id of an order assigned to a given drone in drone assignment
    order_id = drone_cursor.execute("SELECT order_id FROM drone_assignment WHERE drone_id is (?)", [drone_id]).fetchall()
    return order_id[0][0]

def droneDeliveryComplete(drone_id): #When a drone finishes an order this function should run, unassigns the given drone and sets the order's delivery status to "delivered"
    order_id = getAssignedDroneOrder(drone_id)
    unassignDrone(drone_id)
    changeDroneDeliveryStatus(order_id, "delivered")

def site_row_TO_drone_row(site_row): #Reformats a row from Site Order to Drone Order, Used when a row from site order needs to be copied over to drone order
    drone_order_row = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    for i in range(0,len(site_row)):
        drone_order_row[i] = site_row[i]
    drone_order_row[14] = 'waiting'
    return drone_order_row

def updateDroneDb(): #Checks if any drone deliverable orders in Site Orders are in Drone order, if not it copies over the order into drone order

    def isExistingRow(site_row): #Checks if given site_row is already in drone order table
        for i in range(0,len(drone_rows)):
            if(site_row[0] == drone_rows[i][0]):
                return True
        return False

    for i in range(0,len(site_rows)):
        if(isExistingRow(site_rows[i])):
            continue
        addDroneOrderRow(site_row_TO_drone_row(site_rows[i]))

def instantiateDrones(droneAmount): #Creates drones up to the specified amount inside drone assignment table, retains information from previously created drones

    def droneExists(droneID): #Checks if give droneID is already in drone assignmnet table
        for i in range(0, len(drone_assignment_rows)):
            if(droneID == drone_assignment_rows[i][0]):
                return True
        return False

    for i in range(1,droneAmount + 1):
        if(droneExists(i)):
            continue
        drone_cursor.execute("INSERT INTO drone_assignment (drone_id) VALUES (?)", [i])

def assignDroneOrders(): #Assigns orders in Drone Order table to drones in drone assignment table
    droneAmount = 20
    instantiateDrones(droneAmount)

    availableDronesRows = getUnassignedDroneRows()
    availableOrdersRows = drone_cursor.execute("SELECT * FROM drone_order WHERE delivery_status IS 'waiting'").fetchall()
    availableDronesNum = len(availableDronesRows)
    availableOrdersNum = len(availableOrdersRows)

    for i in range(0, availableDronesNum):
        if(availableOrdersNum <= i):
            break
        assignDrone(availableDronesRows[i][0], availableOrdersRows[i][0])
        changeDroneDeliveryStatus(availableOrdersRows[i][0], "busy")

def resetDroneAssignmentTable(): #Clears the drone assignment table, used for debugging
    drone_cursor.execute("DELETE FROM 'drone_assignment'")
    for i in range(0, len(drone_rows)):
        changeDroneDeliveryStatus(drone_rows[i][0], "waiting")

updateDroneDb()
assignDroneOrders()
# resetDroneAssignmentTable()

drone_orders.commit()
drone_orders.close()
site_orders.close()
