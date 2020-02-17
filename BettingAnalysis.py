#To run this project the user only has to change location_of_csv

# Turnover is 3418816.8697053757
# Total EV is 132592.314057336
# Total PnL is 1149187.79505626817
# Total Commission is 72933.80895367861
# Total Net PnL is 76253.98610258955
# RoI is 2.2304203181599753%

#From the monte carlo simulation the edge is 50.98608469316248% after (approx) 10000 games

import pandas as pd
import random
import numpy as np

'''This class is creates and manages each specific horse'''
class horse:
    def __init__(self, race_number, saddle_number, win_fair_price, win_starting_price,winner):
        self.race_number = race_number
        self.saddle_number = saddle_number
        self.win_fair_price = win_fair_price
        self.win_starting_price = win_starting_price
        self.winner = winner

    def calculateOverlay(self):
        '''
        This function calculates the overlay of each bet. The overlay of a bet
        is the (actual % odds)*(market price) - 1 = (1 / win_fair_price)*win_starting_price
        - 1
        '''
        return(1/self.win_fair_price * self.win_starting_price - 1)

    def calculateStake(self, overlay, BankRoll):
        '''
        This function calculates our stake using the Kelly Criterion,
        note that we have set the bank roll for each for each horse to 10000,
        but this can be changed in main()
        '''
        stake = abs(overlay)/(self.win_starting_price-1)*BankRoll
        return(stake)

    def calculateRoI(self, stake, PnL):
        '''
        The Return or Investment for a specific horse will be the PnL for that
        horse divided by the amount we 'bet', i.e. the stake
        '''
        return(PnL/stake * 100)

def UniqueWinner(NumberOfWinners, Count):
    '''This function returns False is a race has more than 1 winner, and
    print that the race has more than one winner, and informs the Users
    that the race will be removed from the data'''
    if NumberOfWinners != 1:
        print('race ' + str(Count)+ ' has multiple winners - deleted')
        return(False)
    return(True)

def ProbsSumToOne(SumOfProbs, raceID):
    '''This functions sums the probabilities of each race and checked if they
    approximately sum to 1. Ths quantities we sum are 1/fair_prices'''
    if not abs(SumOfProbs-1)<0.001 and x_i!=0:
        print('for race ' + str(raceID) + ' fair probs dont sum to 1 - delted')
        return(False)
    return(True)

def main():
    #This will need to changed by the user to the location of horses.csv
    location_of_csv = "/Users/devensethi/Desktop/WSD/"

    #The columns in the CSV file should be: race_number, saddle_number, win_fair_price, win_starting_ price,winner
    #df is the data frame given by horses.csv
    df = pd.read_csv(location_of_csv + "horses.csv")

    '''
    We first check the data has no errors or discrepencies in it.
    N is the total number of races, for each race we check that there is
    only a single winner and the sum of the probabilities such to 1.
    List_N is a list of the races which have a unique winner (not used until the Monte Carlo)
    '''

    N = df['race_number'].max()
    a = np.arange(10000).reshape(2500,4)
    List_N = [i for i in range(1,N+1)]
    #This for loop isn't very efficient, however, I couldn't see how it could be imporved upon
    InvalidRace = []
    df['fair_decimal_odds'] = 1 / df['win_fair_price']
    for i, j, k, l in a:
        NumberOfWinners_i= len(df.loc[(df['race_number']== i+1) & (df['winner']== 1)])
        if UniqueWinner(NumberOfWinners_i, i+1) == False:
            InvalidRace.append(i+1)
        x_i = df.loc[df['race_number'] == i+1, 'fair_decimal_odds'].sum()
        if ProbsSumToOne(x_i, i+1)==False and x_i!=0:
            InvalidRace.append(i+1)

        NumberOfWinners_j= len(df.loc[(df['race_number']== j+1) & (df['winner']== 1)])
        #UniqueWinner(NumberOfWinners_j, j+1)
        if UniqueWinner(NumberOfWinners_j, j+1) == False:
            InvalidRace.append(j+1)
        x_j = df.loc[df['race_number'] == j+1, 'fair_decimal_odds'].sum()
        if ProbsSumToOne(x_j, j+1)==False and x_j!=0:
            InvalidRace.append(j+1)

        NumberOfWinners_k= len(df.loc[(df['race_number']== k+1) & (df['winner']== 1)])
        #UniqueWinner(NumberOfWinners_k, k+1)
        if UniqueWinner(NumberOfWinners_k, k+1)==False:
            InvalidRace.append(k+1)
        x_k = df.loc[df['race_number'] == k+1, 'fair_decimal_odds'].sum()
        if ProbsSumToOne(x_k, k+1)==False and x_k!=0:
            InvalidRace.append(k+1)

        NumberOfWinners_l= len(df.loc[(df['race_number']== l+1) & (df['winner']== 1)])
        UniqueWinner(NumberOfWinners_l, l+1)
        if UniqueWinner(NumberOfWinners_l, l+1) == False:
            InvalidRace.append(l+1)
        x_l = df.loc[df['race_number'] == l+1, 'fair_decimal_odds'].sum()
        if ProbsSumToOne(x_l, l+1)==False and x_l!=0:
            InvalidRace.append(l+1)

    for race_number in InvalidRace:
        index = df[df['race_number'] == race_number].index
        df.drop(index , inplace=True)

    #Create an Horse object for which we must define the instance variable which are simply the columns in horses.csv
    Horse = horse(df['race_number'], df['saddle_number'], df['win_fair_price'], df['win_starting_price'], df['winner'])

    #Now we calculate the overlay of each bet on a single horse
    df['overlay'] = Horse.calculateOverlay()

    #If the overlay is positice we back the horse and if it is negative we lay the horse.
    df.loc[df['overlay']>0,  'side'] = 'back'
    df.loc[df['overlay']<=0,  'side'] =  'lay'

    #How that we have the side and the overlay we use this information to calculate our minimum_stake
    #BankRoll for each horse is 10000
    BankRoll = 10000
    df['stake'] = Horse.calculateStake(df['overlay'], BankRoll)

    #The turnover will be the sum over the stake of all the horses for which the
    #stake is greater than the £2
    turnover = df.loc[df['stake']>=2, 'stake'].sum()
    print(turnover)

    #We calculate the EV for EACH horse individually
    #This is given by the abs.value of the overlay * stake, since the overlay is an indication of how inaccurate the markets price is for the bet,
    #and therefore how much we expect to make from it
    #Here we use vectorised operation instead of looping through the results.
    df['EV'] = abs(df['overlay']) * df['stake']

    #The total EV would the be the sum over all of the indiviual horses EV, provided there stake is greater that £2
    Total_EV = df.loc[df['stake']>=2, 'EV'].sum()
    print(Total_EV)

    #Now we calculate the PnL for each individual horse
    #If we back a horse that wins we get our stake back and the payout from the bookmaker
    df.loc[(df['side']=='back') & (df['winner']==1), 'PnL'] = df['stake'] * (df['win_starting_price'] - 1)
    df.loc[(df['side']=='back') & (df['winner']==0), 'PnL'] = -df['stake']
    df.loc[(df['side']=='lay') & (df['winner'] == 1), 'PnL'] = -(df['stake'] * (df['win_starting_price'] - 1))
    df.loc[(df['side']=='lay') & (df['winner'] == 0), 'PnL'] = df['stake']

    Total_PnL = df.loc[df['stake']>=2, 'PnL'].sum()
    print(Total_PnL)

    TotalCommission = 0
    for i in range(1,N+1):
        x = df.loc[(df['race_number'] == i) & (df['stake']>=2), 'PnL'].sum()
        if x>0:
            CommissionFromRace = x*0.05
            TotalCommission = TotalCommission + CommissionFromRace
    print(TotalCommission)

    #Net PnL is is the Commision - sum of all of the indiviual horse PnL's
    Net_PnL = Total_PnL - TotalCommission
    print(Net_PnL)

    #RoI for a particular bet on a horses
    df['RoI'] = Horse.calculateRoI(df['stake'], df['PnL'])

    #for total RoI we use total PnL instead of Net PnL (mainly because that is what the instructions say)
    Total_RoI = Net_PnL / turnover * 100
    print(Total_RoI)

    df.to_csv(location_of_csv + "OutputBetting.csv")

    ''' ********** MONTE CARLO SIMULATION **********'''

    '''
    Assumptions: Race has unique winner, the whole sample space for potiential races
    are the 10000 given in horses.csv for which there is a unique winner, the only
    difference is the horse which wins the race.
    '''

    #step 1: pick a race from random
    #To determine if we have an edge we will select races from random, and within
    #each race we will pick a winner from random and calculate the required outputs
    #and use these outputs to calculate the RoI, and finally we calculate the preportion
    #of entries in the list which have a positive RoI
    List_Of_RoI = []
    Number_Of_Simulations = 10000
    Count_Errors = 0

    for i in range(Number_Of_Simulations):
        #First step is to select a race from the races which has a UNIQUE winner,i.e. from List_N
        random_int = random.choice(List_N)
        Selected_Race = df.loc[df['race_number'] == random_int]

        #df1 is the data frame of the specific race
        df1 = pd.DataFrame(Selected_Race)

        #We want to randomly pick a new winner, so we first set winner to 0 for each horse
        #Then pick a new winner at random, based on the fair_decimal_odds
        df1.loc[(df1['winner'] == 1), 'winner'] = 0
        try:
            winners_index = df1.loc[(df['winner'] == 0)].sample(weights='fair_decimal_odds').index
            df1.loc[winners_index,'winner'] = 1
        except:
            Count_Errors = Count_Errors + 1
            continue

        '''
        at the moment the entries in Selected_Race aren't correct, so we now calculate
        the PnL, commision, net PnL, and the RoI
        '''
        df1.loc[(df1['side']=='back') & (df1['winner']==1), 'PnL'] = df1['stake'] * (df1['win_starting_price'] - 1)
        df1.loc[(df1['side']=='back') & (df1['winner']==0), 'PnL'] = -df1['stake']
        df1.loc[(df1['side']=='lay') & (df1['winner'] == 1), 'PnL'] = -(df1['stake'] * (df1['win_starting_price'] - 1))
        df1.loc[(df1['side']=='lay') & (df1['winner'] == 0), 'PnL'] = df1['stake']

        #We now sum the PnL, and if it is positive the commision we pay is 5%
        Sum_Of_PnL = df1.loc[df1['stake']>=2, 'PnL'].sum()
        Turnover_Of_Race = df1.loc[df1['stake']>=2, 'stake'].sum()
        commision = 0
        if Sum_Of_PnL>=0:
            commision = Sum_Of_PnL * 0.05
        Net_PnL = Sum_Of_PnL - commision
        RoI = Net_PnL / Turnover_Of_Race
        List_Of_RoI.append(RoI)

    Edge = sum(np.array(List_Of_RoI)>0)/(Number_Of_Simulations-Count_Errors)
    print('From the Monte Carlo Simulation we have an edge of ' + str(Edge))

main()
