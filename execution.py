import safecity_abuse_prediction_pipeline as pp

# user input
abuse_text = str(input())

print('\n')

# run the pipe line
abuse_type = pp.predict_abuse_type(text = abuse_text)
