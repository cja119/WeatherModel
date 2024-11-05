class AuthenticationError(RuntimeError):
        '''Still Failed to authenticate with EarthData. Try again, or check for issues with EarthData online.'''
        pass

class DataCollectionError(RuntimeError):
        ''' Error collecting data, ensure that there are no errors in data presentation
            Date and Time format: "YYYY-MM-DD", type = np.datetime64
            '''
        pass

class WSDataFeedError(RuntimeError):
        ''' It appears that both wind and solar data are set to false. Thus, no data can be returned. 
        '''
        pass