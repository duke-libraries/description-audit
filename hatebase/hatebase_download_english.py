import requests
import json
import pandas as pd

# URL of the authentication endpoint 
auth_url = "https://api.hatebase.org/4-4/authenticate"

# initialize authentication payload & headers
# use x-www-form-urlencoded as content-type 
# replace this dummy key with your own
auth_payload = "api_key=[API KEY GOES HERE]"
headers = {
    'Content-Type': "application/x-www-form-urlencoded",
    'cache-control': "no-cache"
    }

# authenticate against the API
auth_resp = requests.request("POST", auth_url, data=auth_payload, headers=headers)
print (auth_resp.json())
#store the token from response
token = auth_resp.json()["result"]["token"]

#Set vocab url and params
vocab_url = 'https://api.hatebase.org/4-4/get_vocabulary'
lang = 'eng'
resp_format = 'json'


# assemble the payload for our query
vocab_payload = "token=" + token + "&format=" + resp_format + "&language=" + lang
voc_resp = requests.request("POST", vocab_url, data=vocab_payload, headers=headers)

voc_json = voc_resp.json()

pages = voc_json['number_of_pages']
results = voc_json['number_of_results']

# create the vocabulary dataframe from the first resultset
df_voc = pd.DataFrame(voc_json["result"])

#create empty term list
english_term_list = []

# now get results of all the remaining pages 
# append those results to our dataframe "df_voc"
for page in range(1,pages+1):
    vocab_payload = "token=" + token + "&format=json&language=" + lang + "&page=" + str(page)
    voc_resp = requests.request("POST", vocab_url, data=vocab_payload, headers=headers)
    voc_json = voc_resp.json()
    df_voc = df_voc.append(voc_json["result"])
    english_term_list


# reset the df_voc index so that all entries are nicely numbered in an ascending way
df_voc.reset_index(drop=True, inplace=True)

#Full Term List
term_list = df_voc['term'].tolist()

#Filter frame to rows where terms are marked unambiguous
unambiguous_df = df_voc[df_voc['is_unambiguous'] == True]
unambiguous_term_list = unambiguous_df['term'].tolist()

print (unambiguous_term_list)

# save the vocabulary in the df_voc dataframe as a csv 
df_voc.to_csv("c:/users/nh48/desktop/audit_test/hatebase_vocab.csv")
unambiguous_df.to_csv("c:/users/nh48/desktop/audit_test/hatebase_vocab_unambiguous.csv")