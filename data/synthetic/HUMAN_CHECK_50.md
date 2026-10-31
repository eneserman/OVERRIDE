# Human check of 50 synthetic records

Sample: 50 of 240, `random.Random(20261101).sample` over `data/synthetic/synthetic_v1.jsonl`, sorted by id.
Each reviewer fills both columns alone: **Natural?** (would a real user say this here?) and **Labels OK?** (are the spans right under guideline v0.2.3?). Write Y or N, add a note when N.

| # | ID | Last system turn | Synthetic user turn | Spans | Natural? A | Labels OK? A | Natural? B | Labels OK? B | Note |
|---|---|---|---|---|---|---|---|---|---|
| 1 | SYN-0000 | please confirm your reservation for 2 people at everest kitchen in albany on march 1st at 10:30 am | wait, make it for 3 people and push it to 11 am | 3 people = NEW_VALUE; 11 am = NEW_VALUE; make it = UPDATE_CUE; push it = UPDATE_CUE |  |  |  |  |  |
| 2 | SYN-0001 | No problem. I see the average temperature for that day should be 64 degrees. Be advised there is a 26 percent chance of rain. | Hmm, what about the day after instead? | the day after = NEW_VALUE; instead = UPDATE_CUE |  |  |  |  |  |
| 3 | SYN-0006 | Please confirm to book 1 room at Renaissance New York Hotel 57 in New York from March 7th to March 13th. | Let's switch the check-out to March 11th, everything else stays as is. | March 11th = NEW_VALUE; switch = UPDATE_CUE |  |  |  |  |  |
| 4 | SYN-0007 | Okay, confirm the following details: you will pick up the car at Salesforce Transit Center on March 7th at 12 pm and return it on March 8th. The car is a Standard. | Can I bring it back a day later, on the 9th? | the 9th = NEW_VALUE |  |  |  |  |  |
| 5 | SYN-0011 | There's a bus with 0 transfers leaving 6:40 am for $29. | Rather than 6:40, is there anything leaving around noon? | 6:40 = OLD_VALUE; noon = NEW_VALUE; Rather than = UPDATE_CUE |  |  |  |  |  |
| 6 | SYN-0012 | Playing Boyfriend on TV. | Thanks, that's all I needed. | (none) |  |  |  |  |  |
| 7 | SYN-0015 | Here's 1. It is called Breakthrough. | On second thought, a comedy would be better tonight. | a comedy = NEW_VALUE; On second thought = UPDATE_CUE |  |  |  |  |  |
| 8 | SYN-0023 | La Boom is hosting Americo, which many like, this March 8th at 8 pm. | Not that one. Anything in Brooklyn on the same night? | Brooklyn = NEW_VALUE; the same night = REFERENCE |  |  |  |  |  |
| 9 | SYN-0026 | Could you confirm that you will pick up compact car from Charles de Gaulle International Airport on March 2nd at 5 pm and that you will drop it off on March 5th? | Almost. Make the pickup 6 pm rather than 5 pm. | 6 pm = NEW_VALUE; 5 pm = OLD_VALUE; Make = UPDATE_CUE; rather than = UPDATE_CUE |  |  |  |  |  |
| 10 | SYN-0027 | Aka University City is a great 3 star hotel. | Sounds okay. How far is it from the airport? | (none) |  |  |  |  |  |
| 11 | SYN-0029 | Let me make sure this is correct. You want an appointment with Rutherford Dental Lab, next Friday at 11:15 am? | No, I said the 8th of March, not next Friday. | the 8th of March = NEW_VALUE; next Friday = OLD_VALUE |  |  |  |  |  |
| 12 | SYN-0032 | The esscalation music festival is taking place on 5 days here. There is one on march 1st at the melrose ballroom | keep looking, I want something smaller | (none) |  |  |  |  |  |
| 13 | SYN-0034 | Will you please confirm the details of the reservation? You will be booking 1 room at the AC Hotel by Marriott Beverly Hills in Los Angeles beginning on March 3rd and ending on March 7th. | Oops, the end date should be March 8th. | March 8th = NEW_VALUE |  |  |  |  |  |
| 14 | SYN-0036 | book, appoinment with amazing smile dental, appointment is at 12:30 pm appointment is on march 10th | yes thats it | (none) |  |  |  |  |  |
| 15 | SYN-0040 | There is a 4.4 rated Courtyard by Marriott long beach airport. | Hmm, can I see the previous one again? | the previous one = REFERENCE |  |  |  |  |  |
| 16 | SYN-0046 | Please confirm the following the event name is hair care and is scheduled on March 8th at at 6:30 pm. the location is 6790 mckinley street #180 | Change the time to 7 pm, the address is right. | 7 pm = NEW_VALUE; Change = UPDATE_CUE |  |  |  |  |  |
| 17 | SYN-0047 | There are 10 places of interest. You can give a look at American Church in Paris, its a place of worship | Anything that's a museum? | a museum = NEW_VALUE |  |  |  |  |  |
| 18 | SYN-0056 | To confirm then the event is called Restaurant reservation at Akiko's Sushi Bar at 7 pm on March 8th and the location is 542 A Mason Street. | Correct, go ahead. | (none) |  |  |  |  |  |
| 19 | SYN-0061 | Would you like Martin Garrix with song High On Life from album The Martin Garrix Experience? | Sure, play it. | (none) |  |  |  |  |  |
| 20 | SYN-0063 | How about a 3 bedroom, 2 bath apartment at City Walk Apartment Homes at 1688 Clayton Road? It's $3,550 per month. | Any with 2 bathrooms in the same area? | 2 bathrooms = NEW_VALUE; the same area = REFERENCE |  |  |  |  |  |
| 21 | SYN-0070 | Alchemy John MD is a general practitioner in Santa Rosa. | Is there one closer to Petaluma? | Petaluma = NEW_VALUE |  |  |  |  |  |
| 22 | SYN-0076 | Search revealed 10 songs. Do you like Why So Serious by Alice Merton in the Mint album? | nah skip it | (none) |  |  |  |  |  |
| 23 | SYN-0078 | There are 10 restaurants you might like. There is 2g Japanese Brasserie in San Francisco. | Something cheaper in the same city? | the same city = REFERENCE |  |  |  |  |  |
| 24 | SYN-0083 | There are Economy tickets available for $28 on the 10:10 am bus. | Let's take that 10:10 bus, but make it 2 tickets. | that 10:10 bus = REFERENCE; 2 tickets = NEW_VALUE; make it = UPDATE_CUE |  |  |  |  |  |
| 25 | SYN-0084 | The current balance in your checking account is $17,668.68. | Great, thanks for checking. | (none) |  |  |  |  |  |
| 26 | SYN-0087 | There is a great place in Americana at 707 Continental Circle. It's a 1 bed/ 2 bath that's renting for $2,700 a month. | I'd want 2 bedrooms there instead. | 2 bedrooms = NEW_VALUE; instead = UPDATE_CUE |  |  |  |  |  |
| 27 | SYN-0090 | A-1 Dental Care in San Jose. | San Jose is too far, try Santa Clara. | San Jose = OLD_VALUE; Santa Clara = NEW_VALUE |  |  |  |  |  |
| 28 | SYN-0099 | There is compact, Honda Fit, at Intercity Terminal that will be available for pickup on March 8th. | Can I pick that Honda Fit up on the 7th instead? | that Honda Fit = REFERENCE; the 7th = NEW_VALUE; instead = UPDATE_CUE |  |  |  |  |  |
| 29 | SYN-0100 | I have a Tourist Attraction called Cars Land. | My kids love cars, that's perfect. | (none) |  |  |  |  |  |
| 30 | SYN-0105 | Well I also have Abazari Mina MD who is a general practitioner in San Francisco. | Sure, how about the same doctor next week? | the same doctor = REFERENCE; next week = NEW_VALUE |  |  |  |  |  |
| 31 | SYN-0114 | Confirm 1 economy bus leaving Sacramento, CA 1:30 pm to Las Vegas on March 2nd. | Correct, but make that 2 tickets. | 2 tickets = NEW_VALUE; make that = UPDATE_CUE |  |  |  |  |  |
| 32 | SYN-0125 | There is a bus leaving at 7:40 am and the cost is $50 and there is 0 transfer. | Hmm, can you find something that leaves after 10? | after 10 = NEW_VALUE |  |  |  |  |  |
| 33 | SYN-0126 | There are 2 flights that will fit you. Delta Airlines flight takes off at 12:20 pm and return flight departs at 3:20 am costing you $229. | I'd rather fly out of Reno, same dates. | Reno = NEW_VALUE; same dates = REFERENCE |  |  |  |  |  |
| 34 | SYN-0143 | Okay, please confirm that you'd like to book an appointment with Bay Area Obstetrics & Gynecology at 11 am on March 3rd. | Oh shoot, can we push that to 11:30? | 11:30 = NEW_VALUE; push = UPDATE_CUE |  |  |  |  |  |
| 35 | SYN-0159 | Please confirm these details: You want to book an appointment at Atelier Salon Willow Glen on March 12th. The appointment time will be at 5:45 pm. | Oops, it should be 5:15 pm. | 5:15 pm = NEW_VALUE |  |  |  |  |  |
| 36 | SYN-0161 | I found 10 movies you may like. How about Dogman, Hackers, or High Life? | High Life, please. | High Life = NEW_VALUE |  |  |  |  |  |
| 37 | SYN-0166 | Okay. There are 9 hotels available. Do you want to go for the Ace Hotel London? This hotel has a 4.3 rating. | Does it allow dogs? | (none) |  |  |  |  |  |
| 38 | SYN-0175 | Sure no problem. So to confirm: You would like 1 economy ticket on An American Airlines flight leaving from Mexico City to Portland on March 2nd at 7:25 pm. The return flight leaves at 7:20 am on March 14th. | Right, but make the return March 15th. | March 15th = NEW_VALUE; make = UPDATE_CUE |  |  |  |  |  |
| 39 | SYN-0177 | This is 1 option and it is a United Airlines flight that departs at 12:05 pm and the turning flight departs a 10:05 pm for $291. | Do you have the same flight with a morning return? | the same flight = REFERENCE; a morning return = NEW_VALUE |  |  |  |  |  |
| 40 | SYN-0188 | Confirm the following details: You're flying from San Francisco to London at 7 am on American Airlines the day after tomorrow. You're returning on March 13th, and the return flight leaves at 0:45 am. The ticket is for 1 person in Economy class. | That return time is awful, is there one later on the same day? | one later = NEW_VALUE; the same day = REFERENCE |  |  |  |  |  |
| 41 | SYN-0195 | There is a match between Dodgers vs Cubs at the Dodger Stadium. | Ok, is there anything else on that weekend? | that weekend = REFERENCE |  |  |  |  |  |
| 42 | SYN-0196 | There's also the nice 12, Mangalam Place, Sector 3, Rohini, New Delhi rated at 4.1 | Hmm, not sure. Show me the previous one again. | the previous one = REFERENCE |  |  |  |  |  |
| 43 | SYN-0200 | Found 1 flight with American Airlines which takes off at 8:30 am and has 1 stop. The ticket cost will be $278. How about that? | Is there a nonstop one from LA on the same day? | a nonstop one = NEW_VALUE; the same day = REFERENCE |  |  |  |  |  |
| 44 | SYN-0202 | I've found 1 nice Full-size Forester model available for pickup from YVR International Airport next Thursday. | A Forester is too big. Is there a compact one at the same airport? | a compact one = NEW_VALUE; the same airport = REFERENCE |  |  |  |  |  |
| 45 | SYN-0213 | The balance of your checking account is $7,194.51. | Thanks, that is all I wanted. | (none) |  |  |  |  |  |
| 46 | SYN-0214 | There are 3 possibilities for you. There is a full-size Ford Escape ready on March 1st from SFO International Airport. | Is there a cheaper car at the same airport? | a cheaper car = NEW_VALUE; the same airport = REFERENCE |  |  |  |  |  |
| 47 | SYN-0215 | You would like a 1 seat on a luxury ride to 542 A Mason street? | Hmm, too pricey, switch it to a pool ride. | a pool ride = NEW_VALUE; switch = UPDATE_CUE |  |  |  |  |  |
| 48 | SYN-0220 | There is a Alaska Airlines flight. The outbound flight leaves at 7:25 am. The return flight leaves at 1:55 pm. The price of the ticket is $173. | I'd rather come back on the 9th, can you check? | the 9th = NEW_VALUE |  |  |  |  |  |
| 49 | SYN-0228 | The average temperature will be 93 degrees and there's a 12 percent chance of rain. | Hmm, what about Oakland instead? | Oakland = NEW_VALUE; instead = UPDATE_CUE |  |  |  |  |  |
| 50 | SYN-0238 | There is a show 9:30 pm in Century Vallejo 14. | Is there a matinee on the same day? | a matinee = NEW_VALUE; the same day = REFERENCE |  |  |  |  |  |
