from pymongo import MongoClient
from pprint import pprint  # for "pretty printing"
from bson import ObjectId


def connect():
    CONNECTION_STRING = "mongodb://localhost:27017"
    client = MongoClient(CONNECTION_STRING)
    # change this string to match the name of the database you created in Mongo
    return client['project3']



if __name__ == "__main__":
    db = connect()

    # The Python API for working with Mongo is very similar to in the Mongosh shell.
    # However, we must use dictionary indexing like "db['customers']" instead of "db.customers".

    # This is unnecessary, but I like to separate the pipeline stages from the actual aggregate function call.

    cont = True
    while(cont):
        option = input("Main Menu\n1. Employee Lookup\n2. Session Schedule Summary\n3. Unit Report\nEnter any other value to quit\nEnter: ")

        if option == '1':
            employee_name = input("Enter an employee's name: ")

            first, last = employee_name.split()
            employee_lookup = [
                {
                    '$match': {
                        'firstName': first, 
                        'lastName': last
                    }
                }
            ]

    # Run the pipeline.
            results = db["employees"].aggregate(employee_lookup)
    
    #print a "summary" view: their ID, full name, wage; and for each session they are working,
    #the the title of that session, the employee's staff name for the session, 
    #and the name of the unit they are supervising
            for employee in results:
                print(f"Summary:\nID: {employee['_id']}\nFull Name: {employee['firstName']} {employee['lastName']}\nWage: {employee['wage']}\nSession: {employee['sessions'][0].get('sessionTitle')}\nStaff Name: {employee['sessions'][0].get('campName')}\n")
                try:
                    print(f"Unit: {employee['unitId']} and {employee['unitName']}")
                except KeyError:
                    print("No units")

        #Retrieve all scheduled activities for that specific activity at that specific session. 
        #For each scheduling of the activity, print out the title of the rotation it is scheduled during, 
        #the camp name of the staff that is supervising, and the name of the unit that is participating

        if option == '2':
            session_id = input("Enter session ID: ")
            activity = input("Enter activity name: ")

            session_activity_lookup = [
                {
                    '$match': {
                        'sessionId': ObjectId(session_id)
                    }
                }, {
                    '$unwind': {
                        'path': '$schedule'
                    }
                }, {
                    '$match': {
                        'schedule.activityName': activity
                    }
                }
            ]

            results = db["rotations"].aggregate(session_activity_lookup)

            for rotations in results:
                print(f"Summary for {activity}\nTitle: {rotations['title']}\nCamp Name: {rotations['schedule'].get('staffCampName')}\n")
        
        #Input the name of a unit and the name of a session. Print out a summary of that unit at the session: 
        #the name of the unit, and the number of minutes at each different activity during the session. 
        #(That is, if Unit A scheduled Archery at Monday Morning (9-11am) and Tuesday Afternoon (2-3pm), 
        #they spent 180 total minutes at Archery.)
        if option == '3':
            sessionTitle = input("Enter the session title to look up: ")
            unitName = input("Enter the unit name to look up in the session: ")

            unit_lookup = [
                {
                    '$match': {
                        'title': sessionTitle
                    }
                }, {
                    '$unwind': {
                        'path': '$units'
                    }
                }, {
                    '$lookup': {
                        'from': 'rotations', 
                        'localField': 'units._id', 
                        'foreignField': 'schedule.unitId', 
                        'as': 'unitRotations'
                    }
                }, {
                    '$unwind': {
                        'path': '$unitRotations'
                    }
                }, {
                    '$unwind': {
                        'path': '$unitRotations.schedule'
                            }
                }, {
                    '$match': {
                        'unitRotations.schedule.unitName': unitName
                    }
                }, {
                    '$project': {
                        'activityName': '$unitRotations.schedule.activityName', 
                        'duration': {
                            '$divide': [
                                {
                                    '$subtract': [
                                        '$unitRotations.endTime', '$unitRotations.startTime'
                                    ]
                                }, 60000
                            ]
                        }
                    }
                }, {
                    '$group': {
                        '_id': '$activityName', 
                        'totalDuration': {
                            '$sum': '$duration'
                        }
                    }
                }
            ]
            results = db["sessions"].aggregate(unit_lookup)

            print(f"Summary\nUnit Name: {unitName}\n")
            for units in results:
                print(f"Activity: {units['_id']} for a total duration of {units['totalDuration']} minutes\n")

        else:
            cont = False
