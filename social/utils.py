from social import jalali
from datetime import datetime
from django.utils import timezone
from ippanel import Client , Error , HTTPError , ResponseCode


def day_to_string_persian(day) :
    try :
        date_tuple = jalali.Gregorian(day).persian_tuple()
        date_string = '{0:04d}/{1:02d}/{2:02d}'.format(date_tuple[0], date_tuple[1], date_tuple[2])
        return date_string
    except :
        return ''


def customize_datetime_format(input_datetime):
    # Ensure that input_datetime is a datetime object
    if not isinstance(input_datetime, datetime):
        raise ValueError("Input must be a datetime object")

    input_datetime = timezone.localtime(input_datetime)

    # Extract date and time parts
    date_part = {"year": input_datetime.year, "month": input_datetime.month, "day": input_datetime.day}
    date_part = day_to_string_persian((date_part['year'] , date_part['month'] , date_part['day']))

    time_part = input_datetime.strftime("%H:%M:%S")

    result = {"date": date_part, "time": time_part}
    return result


def send_call_counseilng_payment_verified(phone_number , name , date , time , lawyer) :
    sms = Client("B-mILNC5m_lJcyISEqGz-WD53wV7W2FaMsrPIyJHZd8=")
    
    try :
        x = sms.send_pattern("f7q7x3dl55xcxsg", "3000505", phone_number, {'name':name , 'date' : date , 'time' : time})
        y = sms.send_pattern("xv33omtffdcjv7j", "3000505", lawyer , {'order':'مشاوره تلفنی' })
        
    except Error as e: # ippanel sms error
        print(f"Error handled => code: {e.code}, message: {e.message}")
        if e.code == ResponseCode.ErrUnprocessableEntity.value:
            for field in e.message:
                print(f"Field: {field} , Errors: {e.message[field]}")
    except HTTPError as e: # http error like network error, not found, ...
        print(f"Error handled => code: {e}")


def send_online_counseilng_payment_verified(phone_number , name , lawyer , lawyer_num) :
    sms = Client("B-mILNC5m_lJcyISEqGz-WD53wV7W2FaMsrPIyJHZd8=")
    try :
        x = sms.send_pattern("cq1ssbazik9ow5r", "3000505", phone_number, {'name' : name , 'lawyer' : lawyer})
        y = sms.send_pattern("3ej5t4uawmr0hwn", "3000505", lawyer_num, {'lawyer' : lawyer, 'order':'مشاوره آنلاین' })

    except Error as e: # ippanel sms error
        print(f"Error handled => code: {e.code}, message: {e.message}")
        if e.code == ResponseCode.ErrUnprocessableEntity.value:
            for field in e.message:
                print(f"Field: {field} , Errors: {e.message[field]}")
    except HTTPError as e: # http error like network error, not found, ...
        print(f"Error handled => code: {e}")

# chat section

def send_new_message_available_onlin_counseling(phone_number , name , link):
    sms = Client("B-mILNC5m_lJcyISEqGz-WD53wV7W2FaMsrPIyJHZd8=")
    print(phone_number , link , name)
    try :
        x = sms.send_pattern("u9ugni8uq9z2y1f", "3000505", phone_number, {'name' : name , 'link' : link})

    except Error as e: # ippanel sms error
        print(f"Error handled => code: {e.code}, message: {e.message}")
        if e.code == ResponseCode.ErrUnprocessableEntity.value:
            for field in e.message:
                print(f"Field: {field} , Errors: {e.message[field]}")
    except HTTPError as e: # http error like network error, not found, ...
        print(f"Error handled => code: {e}")


def send_new_message_available_free_counseling(phone_number ,name, link):
    sms = Client("B-mILNC5m_lJcyISEqGz-WD53wV7W2FaMsrPIyJHZd8=")
    
    try :
        x = sms.send_pattern("u9ugni8uq9z2y1f", "3000505", phone_number, {'name' : name , 'link' : link})
    except Error as e: # ippanel sms error
        print(f"Error handled => code: {e.code}, message: {e.message}")
        if e.code == ResponseCode.ErrUnprocessableEntity.value:
            for field in e.message:
                print(f"Field: {field} , Errors: {e.message[field]}")
    except HTTPError as e: # http error like network error, not found, ...
        print(f"Error handled => code: {e}")


def send_new_message_available_complaint_counseling(phone_number ,name, link):
    sms = Client("B-mILNC5m_lJcyISEqGz-WD53wV7W2FaMsrPIyJHZd8=")
    
    try :
        x = sms.send_pattern("u9ugni8uq9z2y1f", "3000505", phone_number, {'name' : name , 'link' : link})
    except Error as e: # ippanel sms error
        print(f"Error handled => code: {e.code}, message: {e.message}")
        if e.code == ResponseCode.ErrUnprocessableEntity.value:
            for field in e.message:
                print(f"Field: {field} , Errors: {e.message[field]}")
    except HTTPError as e: # http error like network error, not found, ...
        print(f"Error handled => code: {e}")


def send_new_message_available_contract_counseling(phone_number ,name, link):
    sms = Client("B-mILNC5m_lJcyISEqGz-WD53wV7W2FaMsrPIyJHZd8=")
    
    try :
        x = sms.send_pattern("u9ugni8uq9z2y1f", "3000505", phone_number, {'name' : name , 'link' : link})
    except Error as e: # ippanel sms error
        print(f"Error handled => code: {e.code}, message: {e.message}")
        if e.code == ResponseCode.ErrUnprocessableEntity.value:
            for field in e.message:
                print(f"Field: {field} , Errors: {e.message[field]}")
    except HTTPError as e: # http error like network error, not found, ...
        print(f"Error handled => code: {e}")


def send_new_message_available_legal_pannel(phone_number ,name, link):
    sms = Client("B-mILNC5m_lJcyISEqGz-WD53wV7W2FaMsrPIyJHZd8=")

    try :
        x = sms.send_pattern("luxtwtu3ifotjba", "3000505", phone_number, {'name' : name , 'link' : link})
    except Error as e: # ippanel sms error
        print(f"Error handled => code: {e.code}, message: {e.message}")
        if e.code == ResponseCode.ErrUnprocessableEntity.value:
            for field in e.message:
                print(f"Field: {field} , Errors: {e.message[field]}")
    except HTTPError as e: # http error like network error, not found, ...
        print(f"Error handled => code: {e}")

def send_comment_req(phone_number ,name,service,lawyer, link):
    sms = Client("B-mILNC5m_lJcyISEqGz-WD53wV7W2FaMsrPIyJHZd8=")

    try :
        x = sms.send_pattern("6tv1wrg2vi0qbxh", "3000505", phone_number, {'name' : name ,'service':service,'lawyer':lawyer, 'link' : link})
    except Error as e: # ippanel sms error
        print(f"Error handled => code: {e.code}, message: {e.message}")
        if e.code == ResponseCode.ErrUnprocessableEntity.value:
            for field in e.message:
                print(f"Field: {field} , Errors: {e.message[field]}")
    except HTTPError as e: # http error like network error, not found, ...
        print(f"Error handled => code: {e}")        

def send_call_acc(phone_number ,lawyer,time,num):
    sms = Client("B-mILNC5m_lJcyISEqGz-WD53wV7W2FaMsrPIyJHZd8=")

    try :
        x = sms.send_pattern("w26fiuxp99o950k", "3000505", phone_number, {'laywer':lawyer, 'time' : time, 'num' : num})
    except Error as e: # ippanel sms error
        print(f"Error handled => code: {e.code}, message: {e.message}")
        if e.code == ResponseCode.ErrUnprocessableEntity.value:
            for field in e.message:
                print(f"Field: {field} , Errors: {e.message[field]}")
    except HTTPError as e: # http error like network error, not found, ...
        print(f"Error handled => code: {e}")                