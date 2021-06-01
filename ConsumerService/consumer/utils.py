ACTIONS=['start', 'cancel_start', 'stop', 'cancel_stop']  # order is important here. Events will be ordered by this!!!

def calculate_periods(records):
    """
    This method is responsible for calculating the periods from the raw records list.
    First, it sorts the list by medication_name and event_time and action.
    As I want to go over the records once, the sorting ensures the following:
    1. I'm dealing with one medication at a time. So if I encounter a new medication, I know no other events exist for the previous one.
    2. I'm going over the records by their event_time and not how they were received
    3. The order of actions is very important as I need to deal with each case carefully
    """
    
    records.sort(key=lambda item: (item['medication_name'], item['event_time'], ACTIONS.index(item['action'])))  # sort by medication_name AND event_time AND action
    
    ans = {}  # This will hold my answer. A dict with medication_name as key and a list of tuples for periods as value
    start_period = None  # Initialize start period
    current_medication = None  # Initialize current medication
    for record in records:
        if not record:  # safeguard against empty records although consumer should not add to DB in this case
            continue
        action = record['action']
        medication = record['medication_name']
        
        if medication not in ans:  # new medication
            if current_medication and start_period:
                #We have a previous period in progress that have not stopped
                ans[current_medication].append((start_period,))  # Add non-ending period
            ans[medication] = []  # Initialize new list
            start_period = None
            current_medication = medication
        
        if action not in ACTIONS:  # Safeguard against unknown action
            continue

        #Now comes all the validations. Here I'm throwing an exception, but we can also just print an error and continue processing.
        if action == 'cancel_start' and not start_period:  # cancel_start came before start - invalid input
            raise Exception(f'Invalid input: Got cancel_start event for medication {medication} at {record["event_time"]} without a start event first')
        if action == 'cancel_stop' and (start_period or len(ans[medication]) == 0):  # cancel_stop came after start or without a previous period
            raise Exception(f'Invalid input: Got cancel_stop event for medication {medication} at {record["event_time"]} without a stop event first')
        if action == 'start' and start_period:  # start received when already started
            raise Exception(f'Invalid input: Got double start event for medication {medication} at {start_period} and {record["event_time"]}')
        if action == 'stop' and not start_period:  # Stop received without starting
            raise Exception(f'Invalid input: Got stop event for medication {medication} at {record["event_time"]} without a start')

        
        # Switch on action
        if action == 'start':  # Got start event. Set start_period
            # print(f'Starting period of {medication} at {record["event_time"]}')
            start_period = record["event_time"]
        elif action == 'stop':  # Got stop event. Add new period to ans and clear start_period
            # print(f'Stopping period of {medication} at {record["event_time"]}')
            ans[medication].append((start_period, record["event_time"]))
            start_period = None
        elif action == 'cancel_start':  # Got cancel_start, so just clear start_period
            # print(f'Cancel start period of {medication} at {record["event_time"]}')
            start_period = None
        elif action == 'cancel_stop':  # Got cancel_Stop. We need to search for previous period and delete it.
            # print(f'Cancel stop period of {medication} at {record["event_time"]}')
            last_period = ans[medication][-1]
            start_period = last_period[0]  # continue period as if stop never happened
            ans[medication] = ans[medication][:-1]  # Remove last period from answer
    
    if current_medication and start_period:  # in the end, we need to check if period is in progress
        #We have a medication in progress that have not stopped
        ans[current_medication].append((start_period,))
    
    return ans