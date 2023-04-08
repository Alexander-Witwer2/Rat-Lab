# # INSTRUCTIONS: copy/paste this into app.py, stick testSpareRats() and testColonyRats(true), testColonyRats(false)
# # somewhere where they'll be activated, and load that page
# resetDatabaseValues = {
#     "60M" : "75F", # 62F
#     "68M" : "94F", # 62F
#     "79M" : "UNK", # 62F
#     "65M" : "63F", # 62F relative
#     "71M" : "41F", # 76F
#     "75M" : "UNK", # 76F
#     "93M" : "81F", # 76F
#     "80M" : "96F", # 76F relative
#     "74M" : "66F", # 76F relative
#     "71F" : "UNK", # 92M
#     "80F" : "81M", # 92M
#     "97F" : "94M", # 92M
#     "75F" : "60M", # 92M relative
#     "65F" : "45M", # 92M relative
#     "75M" : "UNK", # 101F
#     "81M" : "80F", # 101F
#     "77M" : "86F", # 99F
#     "94M" : "97F"  # 99F
# }

# spare_rat_partners = {
#     "62F" : ['60M', '68M', '79M'],
#     "76F" : ['71M', '75M', '93M'],
#     "92M" : ['71F', '80F', '97F'],
#     "101F" : ['75M', '81M'],
#     "99F" : ['77M', '94M']
# }

# spare_rat_relatives = {
#     "62F" : ['65M'],
#     "76F" : ['80M', '74M'],
#     "92M" : ['75F', '65F'],
#     "101F" : ['80M'],
#     "99F" : []
# }

# correctOutputColonyRatsSwappingPairsTrue = {
#     "41F" : ['60M', '61M', '65M', '66M', '73M', '74M', '75M', '77M', '78M', '79M', '80M', '81M', '82M', '86M', '87M', '93M', '94M'],
#     "59M" : ['63F', '64F', '65F', '71F', '72F', '73F', '74F', '75F', '80F', '81F', '82F', '94F', '95F', '96F', '97F'],
#     "66F" : ['61M', '65M', '66M', '71M', '75M', '78M', '79M', '81M', '82M', '86M', '87M', '93M', '94M'],
#     "83M" : ['61F', '63F', '71F', '72F', '80F', '82F', '94F', '95F', '96F', '97F'],
#     "65F" : ['61M', '65M', '66M', '71M', '75M', '78M', '79M', '81M', '82M', '86M', '87M', '93M', '94M'],
#     "71M" : ['61F', '63F', '64F', '65F', '71F', '72F', '73F', '74F', '82F', '94F', '95F', '96F', '97F'],
#     "81F" : ['61M', '65M', '66M', '75M', '78M', '79M', '81M', '82M', '86M', '87M', '94M'],
#     "80M" : ['61F', '63F', '71F', '72F', '82F', '94F', '95F', '97F'],
#     "94F" : [('60M',), ('61M',), ('65M',), ('66M',), ('71M',), ('73M',), ('74M',), ('75M',), ('77M',), ('78M',), ('79M',), ('80M',), ('81M',), ('82M',), ('86M',), ('87M',), ('93M',), ('94M',)],
#     "78M" : [('61F',), ('63F',), ('64F',), ('65F',), ('71F',), ('72F',), ('73F',), ('74F',), ('75F',), ('80F',), ('81F',), ('82F',), ('94F',), ('95F',), ('96F',), ('97F',)]
# }

# correctOutputColonyRatsSwappingPairsFalse = {
#     "41F" : ['84M', '85M', '88M', '89M', '90M'],
#     "59M" : ['100F', '102F', '103F', '104F', '87F', '88F', '89F', '90F', '98F', '99F'],
#     "66F" : ['84M', '85M'],
#     "83M" : ['100F', '101F', '104F', '106F', '62F', '78F', '79F', '91F', '92F', '99F'],
#     "65F" : ['84M', '85M'],
#     "71M" : ['100F', '102F', '103F', '62F', '76F', '77F', '78F', '79F', '87F', '88F', '89F', '90F', '99F'],
#     "81F" : ['84M', '85M'],
#     "80M" : ['100F', '62F', '78F', '79F', '99F'],
#     "94F" : [('84M',), ('85M',), ('88M',), ('89M',), ('90M',), ('91M',), ('92M',), ('96M',)],
#     "78M" : [('100F',), ('101F',), ('102F',), ('103F',), ('104F',), ('106F',), ('62F',), ('76F',), ('77F',), ('78F',), ('79F',), ('87F',), ('88F',), ('89F',), ('90F',), ('91F',), ('92F',), ('98F',), ('99F',)]
# }

# def testColonyRats(swappingExistingPairs):
#     currently_paired_rats_to_test = ['41F', '59M', '66F', '83M', '65F', '71M', '81F', '80M', '94F', '78M']
#     for rat in currently_paired_rats_to_test:
#         result = pairing(rat, swappingExistingPairs)
#         # print(rat + ": " + str(result))
#         if(swappingExistingPairs == True):
#             if(result == correctOutputColonyRatsSwappingPairsTrue[rat]):
#                 print(rat + " passed")
#             else:
#                 print(rat + " FAILED")
#         else:
#             if(result == correctOutputColonyRatsSwappingPairsFalse[rat]):
#                 print(rat + " passed")
#             else:
#                 print(rat + " FAILED")

# def resetDatabase():
#     for rat in resetDatabaseValues.keys():
#         db.session.execute(db.update(Rat).where(Rat.rat_number == rat).values(current_partner = resetDatabaseValues[rat]))
#     db.session.commit()

# def killRat(rat):
#     # update database to kill off rats to make vacancies
#     db.session.execute(db.update(Rat).where(Rat.rat_number == rat).values(current_partner = "DEC"))
#     db.session.commit()
    
# def testSpareRat(spare_rat, swappingExistingPairs):
    
#     result = pairing(spare_rat, swappingExistingPairs)
#     relatedRatError = "ERROR: there are no unrelated rats that " + spare_rat + " can be paired with"

#     # testing case 1, the "can't swap existing pairs if input rat is a spare rat" error
#     if(swappingExistingPairs == True and result == "ERROR: cannot swap existing pairs if the inputted rat is a spare rat"):
#         print("success: tested " + spare_rat + " with swappingExistingPairs = true for no swapping existing pairs allowed if rat is spare error.  function returned: " + result)

#     # testing case 2a, the no vacancy error
#     elif(swappingExistingPairs == False and result == "ERROR: there are no unpaired rats to pair the given rat with"):
#         print("success: tested " + spare_rat + " with swappingExistingPairs = false and no vacancy in colony.  expecting no vacancy error.  function returned: " + result)
    
#     # testing case 2b, input is a related rat error
#     elif(swappingExistingPairs == False and result == relatedRatError ):
#         print("success. tested " + spare_rat + " with swappingExistingPairs = false, input is related rats. expecting error, function returned: " + str(result))

#     # testing case 2c: succeeded in finding unrelated rat
#     elif(swappingExistingPairs == False and result == spare_rat_partners[spare_rat]):
#         print("success. tested " + spare_rat + " with swappingExistingPairs = false, input is unrelated rats. expecting breeding pool, function returned: " + str(result))
#         #print(spare_rat + " passed, unrelated partner available and swappingExistingPairs = " + str(swappingExistingPairs))
#     else:
#         print(spare_rat + " FAILED")
#     resetDatabase()

# def testSpareRats():
#     for rat in spare_rat_partners.keys():     
#         testSpareRat(rat, True) # case 1: can't swap existing pairs if input is spare rat
#         testSpareRat(rat, False) # case 2a: no vacancy error 
#         for relative in spare_rat_relatives[rat]: 
#             killRat(relative)
#         testSpareRat(rat, False) # case 2b: only vacancy is with a related rat
#         for partner in spare_rat_partners[rat]:
#             killRat(partner)
#         testSpareRat(rat, False) # case 2c: vacancies are with unrelated rats
        
#     def testPairingAlgorithm():
#     resetDatabase()
#     print("TESTING COLONY RATS, SWAPPING = TRUE")
#     testColonyRats(True)
#     print("\nTESTING COLONY RATS, SWAPPING = FALSE")
#     testColonyRats(False)
#     print("\nTESTING SPARE RATS")
#     testSpareRats()