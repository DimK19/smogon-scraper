import SmogonScraper
import matplotlib.pyplot as plt
import json
import pandas

ss = SmogonScraper.SmogonScraper()

with open("smogon_data.txt", 'w') as f:
    # print(self.allGames, file = f)
    json.dump(ss.getRawData(), f)

with open("smogon_data.txt", 'r') as f: data = json.load(f)

# df = pandas.DataFrame(data)    
    
byDateOnly  = {} # ignore different sub-formats
for i in data:
    if i.split('_')[0][:7] not in byDateOnly: byDateOnly.update({i.split('_')[0][:7] : data[i]})
    else: byDateOnly[i.split('_')[0][:7]] += data[i]
    
plt.bar(*zip(*byDateOnly.items()))
plt.xticks(rotation = 90)
plt.tick_params(labelsize = 7) # not good
plt.show()
