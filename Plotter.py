## TODO
## Keep track of last update date, so thst you dont pull all the data with every refresh each time

#import SmogonScraper
import matplotlib.pyplot as plt
import json

#ss = SmogonScraper.SmogonScraper()

#with open("smogon_data.txt", 'w') as f: json.dump(ss.getRawVGCData("vgc"), f)
with open("smogon_data.txt", 'r') as f: data = json.load(f)  

byDateOnly  = {} # ignore different sub-formats
for i in data:
    # i.split('_')[0][:7] this disgusting expression extracts solely the date from the key string
    if(i.split('_')[0][:7] not in byDateOnly): byDateOnly.update({i.split('_')[0][:7] : data[i]})
    else: byDateOnly[i.split('_')[0][:7]] += data[i]
    
plt.bar(*zip(*byDateOnly.items()))
# *zip(*dict.items()) consists of two tuples, one containing the unpacked keys of the dictionary
# and one containing the corresponding unpacked values
plt.xticks(rotation = 90) # Rotate horizontal axis labels by 90 degrees
plt.tick_params(labelsize = 7) # not good
plt.show()
