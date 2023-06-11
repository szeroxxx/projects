invoice_status = (
    ("pending","Pending"),
)

scheduler_status = (
   ("pending","Pending"),
   ("call_due","Call due"),
   ("call_done","Call done"),
   ("in_progress","In progress"),
   ("finished","Finished"),
   ("legal_action","Legal Action"),

)

action_types = (
    ("call","Call"),
    ("email","Email"),
    ("chat","Chat"),
    ("offline_message","Offline message"),
    ("remarks","Remarks"),
    ("follow_up","Follow up"),
    ("call_and_email","Call and email"),
    ("call_and_message","Call and message"),
)

action_status = (
    ("done","Processed"),
    ("due","Follow up"),
    ("completed","Completed"),
    ("finished","Finished"),
    ("pending","Pending"),
)
doc_type = (("general", "General"), ("invoice", "Invoice"), ("order", "Order"))



def base_choices(code):
    if code == "payment_difference_types":
        payment_difference_types = (
            ("OutStanding","Outstanding"),
            ("Bank Charges","Bank Charges"),
            ("Discount","Discount"),
            ("Write Off","Write off"),
            ("OverPaid","OverPaid"),
            ("INVCLOSED","Close"),
        )
        return payment_difference_types
    
    if code == "payments_mode" :
        payments_mode = (
            ("bank","Bank"),
            ("cash","Cash"),
            ("cheque","Cheque"),
            ("credit_card","Credit card"),
            ("paypal","Paypal"),
            ("BT","BT"),
            ("COD","COD"),
            ("CBP","CBP"),
        )
        return payments_mode
    
    if code == "language":
        languages = (
            ("english-us","English-US"),
            ("germen","Germen"),
            ("french", "French"),
            ("dutch","Dutch"),
            ("hungarian", "Hungarian"),
            ("italian","Italian"),
            ("english","English")
        )
        return languages