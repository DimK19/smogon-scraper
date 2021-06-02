import matplotlib.pyplot as plt

class Plotter():
    def plot(self, data):
 
        '''
        byDateOnly  = {} # ignore different sub-formats
        for i in data:
            # i.split('_')[0][:7] this disgusting expression extracts solely the date from the key string
            if(i.split('_')[0][:7] not in byDateOnly): byDateOnly.update({i.split('_')[0][:7] : data[i]})
            else: byDateOnly[i.split('_')[0][:7]] += data[i]
        '''
        
        plt.bar(*zip(*data.items()))
        # *zip(*dict.items()) consists of two tuples, one containing the unpacked keys of the dictionary
        # and one containing the corresponding unpacked values
        plt.xticks(rotation = 90) # Rotate horizontal axis labels by 90 degrees
        plt.tick_params(labelsize = 7) # not good
        plt.show()

## Testing
def main():
    Plotter().plot("vgc")
    
if(__name__  == "__main__"): main()
