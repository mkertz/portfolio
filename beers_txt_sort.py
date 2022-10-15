import re
import string
import openpyxl
from openpyxl.utils import get_column_letter, column_index_from_string
import pickle


def main():
    '''
    This program determines Medicare Part D spending on Beer’s list medications. 
    Medicare Part D is a government sponsored insurance program that covers self-administered medications within elderly populations. 
    Beer's list medications have an elevated potential for adverse effects within elderly populations. 
    This program sorts out Beer’s list medications from the CMS spending and utilization data for Medicare Part D. 
    This also allows for further analysis on the Beer’s list medication data.
    
    '''




    '''
    su_drugs named for spending and utilization
                this has a file of the drugs are in the CMS spending and utilization list drugs, for drugs on Medicare Part D. 
                it came from an excel file put out by CMS, imported into a list using openpyxl
                it is ordered alphabetically with a new drug for each line
                it was converted to a text file for quicker manipulation than directly using openpyxl on excel files
                excel files were loading slowly so this was taken
    su_drugs is a list made from the drugs in su_drugs.txt
    
   '''
    su_drugs = []
    for line in open('input files/su_drugs.txt'):  #each drug is on a line in su_drugs.txt, which converts it to the list su_drugs
        su_drugs.append(line.rstrip('\n'))
    '''
    su drugs has repeat drugs of the same name (for different brand names, same generic) 
    repeats are included for accurrate sums of costs, repeats are used multiple times when different brand names
    '''


    '''
    beers_drugs is a list of drugs on the Beers list, these are drugs which should be avoided in geriatric populations.
    beers 2012.txt is a file of the drugs that are not ordered
    get_list is a program which eliminates duplicates and alphabetically organizes text among other manipulations
        see get_list for more detail
    '''

    beers_drugs = get_list('input files/beers 2012.txt')


    '''
    added_beers is a list of additional beers drugs that were not included in the article beer's list were copied from
    '''
    added_beers = get_list('input files/beers 2012 added terms.txt')
    beers_drugs.extend(added_beers)

    '''
    deleted drugs is a list of drugs which were on Beer's list but were removed due to unneccessary matches
    (for example, insulin is on beer's list, but is to be used in certain ways, and with caution)
    '''

    deleted_drugs = get_list('input files/beers 2012 del terms.txt')
    beers_drugs = remove_terms(beers_drugs, deleted_drugs)


    beers_drugs = list(dict.fromkeys(beers_drugs)) #eliminate duplicates for filtering. beers_drugs can't include duplicates.


    '''
    list1_pattern_list2_match is a code which matches words in list1 with words with list2.
        list1 is beers list, list2 is the drugs in spending and utilization
    
    the following lists were created for identifying errors:
        matched_beers: drugs that were on the beers list that matched.
            There to sort for non-drug terms, like maleate or adult, which could lead to false hits
        unmatched_beers: drugs that were on beers list that weren't matched
            It is here that drugs that weren't matched but are in su_drugs are a concern, eg formerly? trimipramine maleate'
        matched_su: drugs on spending and utilization that were matched. Duplicates should be here
        unmatched_su: drugs on spending and utilization that were not matched.
            no Beers drugs should be here.
    
    indices are the indicies of the list su_drugs that match with Beer's drugs. 
    indices are so drug prices could be calculated in a seperate process than the sort function
        doing so allows for elimination of duplicate calculations, decreases complexity
    
    '''


    matched_beers, unmatched_beers, matched_su, unmatched_su, indices = list1_pattern_list2_match(beers_drugs, su_drugs)

    '''
    beers_sum is the sum of the costs of all drugs on the beers list
    no_beers_sum is the sum of costs of drugs that are not on the beers list
    spending_est estimates the sum of beers and no beers
    '''

    beers_sum, no_beers_sum = spending_est(indices)

    '''
    The remaining segment of main() below is intended to check for errors
    list to file converts lists to text files for scanning after the program is run
    '''
    list_to_file(matched_su, 'output files/su matched.txt')
    list_to_file(unmatched_su, 'output files/su unmatched.txt')
    list_to_file(matched_beers, 'output files/matched beers.txt')
    list_to_file(unmatched_beers, 'output files/unmatched beers.txt')

    '''this is a fraction of medicare part D spending that is spent on beers drugs'''
    print(beers_sum/(beers_sum+no_beers_sum))



def get_list(document):
    '''
    get_list takes a document of text, that could include full sentences, but has the name of Beer's drugs
    the document is copy pasted from an article on updating the Beer's list
    this document contains generic drug names on the beers list as well as other non-drug names
    it's designed to create a list of the drug names and minimize non-drugs names
    non-drug names, such as maleate which could have false hits on su_drugs, could be removed by removal list
    '''
    words = []  #words is a list which will be composed of a document

    filter = re.compile(r'[^a-z]') #this filter is designed to catch and later on sort out non-lowercase-letter characters

    for line in open(document):
        names = line.split()    #collects multiple words which could be on line
        for name in names:      #divides up words on line
            name = name.lower()
            name = filter.sub('', name)     #substitutes out non-lower case characters for nothing
            if len(name) > 4:               #does not take in small non-drug names (drugs names > 4 characters)
                words.append(name)          #each word in line is added to words

    words = list(dict.fromkeys(words))  # delete duplicate words
    words.sort()  # organize alphabetically, done for error checking, as it is easier to sort through files

    return (words)


def remove_terms(terms, deleted_terms):

    '''
    :param terms: terms (Beers list), some of which should be deleted
    :param deleted_terms: words that are deleted from the list terms (drugs on Beers list)
            by customizing deleted_terms, could see different costs without drugs that shouldn't be included on Beer's
    :return: terms are returned minus the deleted terms
    '''

    for i in range(len(deleted_terms)):     #sort through items in deleted_terms that will be deleted from the list terms
        del_pattern = re.compile(r'.*(%s).*' % deleted_terms[i])    #match word patterns, done for longer names, maybe not needed
        j=0
        while j < len(terms):               #cycle through list of terms
            if del_pattern.match(terms[j]): #if pattern of deleted term matches, delete term in index j
                terms.pop(j) #j is now assigned to the next item, and so is not increased (term[j+1] becomes term[j])
            else:   #j increases only if items in list stays in same place (don't decrease as a result of pop function)
                j+=1

    return(terms)



def list1_pattern_list2_match(list1,list2):
    '''
    this program is designed find occurrences of list1 in list2
    items in list1 could occur more than once in list2
        each occurrence is documented
    items in list1 could be part of an item in list2
        this occurrence needs to be documented
    different items in list 1 could hit the same item in list 2, but this is recorded only once
    list2 has repeating items, each repeat is recorded

    for the goals of the program, matched_list2_indices is the only needed return list
        the others lists are included for error checking

    indices keep track of matching occurrences in list 2, as names have repeats
    list2 is preferably in alphabetical order for consistency in indices across programs

    :param list1: single terms that have a pattern that could be in item in list2 (Beer's drugs)
    :param list2: list which could have repeats and combined terms and repeats (su_drugs)
                each matching index is counted once
    :return:
    '''
    matched_list1 = []          #list1 terms that are matched (Beer's list drugs found within list 2)
    unmatched_list1 = []        #list1 terms that are not matched (terms that are not drugs, or unmatched Beer's drugs)
    matched_list2 = []          #could have multiple repeat items,as well as combos
    unmatched_list2 = list2.copy()  #unmatched_list2 are drugs not on list1, formed by deleting matches from list2
    matched_list2_indices = []  #indices of list2 that are matched to list1 (su_drugs on beers_list)

    for i in range(len(list1)):
        list1_pattern = re.compile(r'.*(%s).*' % list1[i])  #pattern matching: list 1 items may be within item in list 2
        match = 0                                           #match keeps track of matches in list1 (Beer's list).
        for j in range(len(list2)):                         #evaluates each list1 pattern to list2
            if list1_pattern.match(list2[j]) and j not in matched_list2_indices: #if index not previously matched
                matched_list2.append(list2[j])              #each item in list2 matched only once
                unmatched_list2.remove(list2[j])            #unmatched list2 formed by deletions from list2
                matched_list2_indices.append(j)             #indices keep track of repeat items in list2
                match = 1                                   #used for list of matching terms in list1
        if match == 1:
            matched_list1.append(list1[i])      #if there is a match, will go to matched_list1
        else:
            unmatched_list1.append(list1[i])


    return(matched_list1, unmatched_list1, matched_list2, unmatched_list2, matched_list2_indices)




def list_to_file(list, file_name):
    '''

    :param list: list is a list that is converted into a txt file
    :param file_name: file_name is the name of the txt file, includes txt extension
    :return: returns the list and the file, (I dont think this is neccessary)
    '''
    list.sort()                 #order alphabetically for ease of scanning
    file = open(file_name, 'w') #write to file
    for i in range(len(list)):
        file.write(list[i])
        file.write('\n')        #create a new line (for easier reading)
    file.close()
    return( list, file )



def spending_est(indices):
    '''
    program is designed to sort through indices which associated list, which comes from a pickled file
        I used a pickled file instead of a txt file because I had trouble reading float from a txt file
        I couldn't figure out a way how to read float from a text file correctly
    :param indices: indicies with spending and utilization of drugs that are on the beers list
        indices used instead of names, due to complications with repeat names of generics on spending and utilization
        repeat names are necessary for costs associated with different brand names but that have the same generic name
        though they have the same name, they are different and so indices keeps track of this
    :return: beers_sum is the amount of money spent on drugs on the indices, that is on beers drugs (minus deletions)
                no_beers_sum is the amount spent on drugs that are not on the beers list
    '''

    with open("input files/spending.txt", "rb") as gp:  #spending.txt contains a pickled list of costs
        spending = pickle.load(gp)          #spending is a list of costs of each drug

    '''
    the indicies of spending correspond with the indicies of drugs
    for example, the cost at spending[7] is the cost of su_drug[7]
    '''


    beers_sum = 0                           #beers_sum and no_beers_sum are talied as the loop progresses
    no_beers_sum = 0
    for i in range(len(spending)):          #goes over each item (float value) in spending list
        if isinstance(spending[i], float):  #some values are non-existant if no cost expenditures, rules these out
            if i in indices:                #if i corresponds to an indice of a Beers drugs add up the cost
                beers_sum += spending[i]
            else:
                no_beers_sum+=spending[i]

    return(beers_sum, no_beers_sum)







if __name__ == "__main__":
    main()

