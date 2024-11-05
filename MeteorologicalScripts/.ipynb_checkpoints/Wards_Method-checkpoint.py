from scipy.spatial.distance import cdist
import numpy as np
import pandas as pd

def update_array(current_array,min_arg,original_array,count,update_strategy='mean'):

    i1 = min_arg
    i2 = len(current_array)-1 if min_arg == 0 else min_arg-1

    l1 = int(current_array[i1][1])
    l2 = int(current_array[i2][1])

    t1 = int(sum([current_array[i][1] for i in range(i1)]))
    t2 = int(sum([current_array[i][1] for i in range(i2)]))

    samples = np.concatenate(([current_array[i1][0]]*int(current_array[i1][1]),[current_array[i2][0]]*int(current_array[i2][1])))

    if update_strategy == 'mean':
        i3 = i1
        l3 = l1+l2
        w3 = np.mean(samples)
        
    if update_strategy == 'median':
        i3 = i1
        l3 = l1+l2
        w3 = np.median(samples)
       

    if update_strategy == 'medoid':
        i3 = i1
        l3 = l1+l2
        w3 = samples[np.argmin(np.sum(cdist([samples],[samples],metric='euclidean')))]
    
        
    if i1 == 0:
        new_array = np.concatenate(([[w3,l3]],current_array[i1+1:i2]))
        count += l2
    else:
        new_array = np.concatenate((current_array[:i2],[[w3,l3]],current_array[i1+1:]))
    return new_array,count

def consecutive_clustering(df,number_of_clusters,update_strategy='medoid'):
    current_array = df.values
    current_array = np.vstack((df.values.reshape(df.shape[0]),np.ones(df.shape[0]))).T
    count = 0
    while len(current_array[:,0]) > number_of_clusters-1:
        
        breakpoint = np.random.randint(0,len(current_array)-1)
        temp_array = np.concatenate((current_array[breakpoint:],current_array[:breakpoint]))
        temp_min_arg = np.argmin(((2*np.abs(temp_array[:,1]) * np.abs(np.insert(temp_array[:-1,1],0,temp_array[-1,1]))))/(np.abs(temp_array[:,1]) + np.abs((np.insert(temp_array[:-1,1],0,temp_array[-1,1]))))*(temp_array[:,0]-np.insert(temp_array[:-1,0],0,temp_array[-1,0]))**2)
        min_arg = temp_min_arg - breakpoint
        if min_arg < 0:
            min_arg += len(current_array)
        current_array,count = update_array(current_array,min_arg,df.values,count,update_strategy)


    current_array[0][1] -= count
    final_array = np.concatenate((current_array,[[current_array[0][0],count]])) 
    return final_array


def compute_objective(predictions, df):
    obj=0
    for i in range(len(predictions)):
        obj += (predictions[i] - df[0][i])**2
    return (float(obj) / len(df))

def save_csv(array,title,folder='PreOptimisationDataStore'):
    if isinstance(array,dict):
        data = array        
        pass
    else:
        data = {i: value for i,value in enumerate(array)}
        
    # Open the file in write mode to empty its content before writing new data
    csv_file = os.path.join(folder, title)
    os.makedirs(folder, exist_ok=True)

    with open(csv_file, mode='w', newline='') as file:
        # Create a writer object
        writer = csv.writer(file)
        
        # Write the header row
        writer.writerow(['Key', 'Value'])
        
        # Write the data rows
        for key, value in data.items():
            writer.writerow([key, value])
