# Human check of 50 synthetic records

Sample: 50 of 1,000, `random.Random(20261101).sample` over `data/synthetic/synthetic_v2.jsonl`, sorted by id.
Each reviewer fills both columns alone: **Natural?** (would a real user say this here?) and **Labels OK?** (are the spans right under guideline v0.2.3?). Write Y or N, add a note when N.

| # | ID | Last system turn | Synthetic user turn | Spans | Natural? A | Labels OK? A | Natural? B | Labels OK? B | Note |
|---|---|---|---|---|---|---|---|---|---|
| 1 | SYN-0001 | No problem. I see the average temperature for that day should be 64 degrees. Be advised there is a 26 percent chance of rain. | Hmm, what about the day after instead? | the day after = NEW_VALUE; instead = UPDATE_CUE |  |  |  |  |  |
| 2 | SYN-0006 | Please confirm to book 1 room at Renaissance New York Hotel 57 in New York from March 7th to March 13th. | Let's switch the check-out to March 11th, everything else stays as is. | March 11th = NEW_VALUE; switch = UPDATE_CUE |  |  |  |  |  |
| 3 | SYN-0026 | Could you confirm that you will pick up compact car from Charles de Gaulle International Airport on March 2nd at 5 pm and that you will drop it off on March 5th? | Almost. Make the pickup 6 pm rather than 5 pm. | 6 pm = NEW_VALUE; 5 pm = OLD_VALUE; Make = UPDATE_CUE; rather than = UPDATE_CUE |  |  |  |  |  |
| 4 | SYN-0029 | Let me make sure this is correct. You want an appointment with Rutherford Dental Lab, next Friday at 11:15 am? | No, I said the 8th of March, not next Friday. | the 8th of March = NEW_VALUE; next Friday = OLD_VALUE |  |  |  |  |  |
| 5 | SYN-0044 | Your savings account balance is $8,157.51. | Thanks. And my checking? | checking = NEW_VALUE |  |  |  |  |  |
| 6 | SYN-0051 | The Best Western Plus Portland Airport Hotel & Suites is a 2 star hotel in the area. | I'd rather stay at a 3 star one. | a 3 star one = NEW_VALUE |  |  |  |  |  |
| 7 | SYN-0061 | Would you like Martin Garrix with song High On Life from album The Martin Garrix Experience? | Sure, play it. | (none) |  |  |  |  |  |
| 8 | SYN-0093 | There is also an American Airlines flight with a 10:25 PM departure and a 7:40 PM return for $154. | Is there a flight with the same return time but leaving in the morning? | the same return time = REFERENCE; the morning = NEW_VALUE |  |  |  |  |  |
| 9 | SYN-0105 | Well I also have Abazari Mina MD who is a general practitioner in San Francisco. | Sure, how about the same doctor next week? | the same doctor = REFERENCE; next week = NEW_VALUE |  |  |  |  |  |
| 10 | SYN-0111 | You want a Luxury cab for 1 person to take you to 18615 California 12. Is that right? | Not luxury, a shared one is fine. | luxury = OLD_VALUE; a shared one = NEW_VALUE |  |  |  |  |  |
| 11 | SYN-0118 | How about the Discovery Children's Museum? | Do I need tickets for that? | (none) |  |  |  |  |  |
| 12 | SYN-0128 | Search revealed 8 results. You can get a Flexible ticket on a bus departing at 8:30 am for $45. | Can I get the Economy one on that bus instead? | the Economy one = NEW_VALUE; that bus = REFERENCE; instead = UPDATE_CUE |  |  |  |  |  |
| 13 | SYN-0139 | You would like 4 economy tickets on a flight leaving on March 1st from New York to Washington on United Airlines? | Hmm, make it premium economy instead. | premium economy = NEW_VALUE; make it = UPDATE_CUE; instead = UPDATE_CUE |  |  |  |  |  |
| 14 | SYN-0145 | I found 1 movie for you. How about Captain Marvel? | Seen it already. Anything else in Imax there? | Imax = NEW_VALUE |  |  |  |  |  |
| 15 | SYN-0160 | They do have a nice standard Toyota Prius. It is also available for pick up today at Dulles International Airport. | Hmm, is that Prius available tomorrow instead of today? | that Prius = REFERENCE; tomorrow = NEW_VALUE; today = OLD_VALUE; instead of = UPDATE_CUE |  |  |  |  |  |
| 16 | SYN-0187 | Ok, to confirm you'd like to go to 3883 Vista Oaks Drive in a cab for 3 people and you want a shared ride. | Hmm, 4 people actually. | 4 people = NEW_VALUE; actually = UPDATE_CUE |  |  |  |  |  |
| 17 | SYN-0190 | I've got 1 showtime. There's a show at 9 pm in Century 25 Union Landing & XD. | Is there anything a bit earlier? | (none) |  |  |  |  |  |
| 18 | SYN-0224 | So you would like me to reserve a Compact car from Heathrow International Airport on March 2nd with a 10:30 am pickup and return of March 7th? | Yes, but pick up at 11:30 instead. | 11:30 = NEW_VALUE; instead = UPDATE_CUE |  |  |  |  |  |
| 19 | SYN-0253 | To confirm: You are staying in Philadelphia with 3 people next Wednesday, with a check out date of March 14th. | We're actually 4 now, my brother joins us. | 4 = NEW_VALUE; actually = UPDATE_CUE |  |  |  |  |  |
| 20 | SYN-0281 | Ok to confirm then it is 4 people leaving from Fresno. | Yes, 4 people from Fresno. | 4 people = NEW_VALUE; Fresno = NEW_VALUE |  |  |  |  |  |
| 21 | SYN-0314 | The Beach Boys concert will also take place at the PNE Amphitheatre on March 9th. | March 9th works, grab me 2 seats. | March 9th = REFERENCE; 2 seats = NEW_VALUE |  |  |  |  |  |
| 22 | SYN-0333 | I can't book that time. How about 5 pm on March 4th at Cosmetic Dentist In Los Gatos - Moradi Signature Smiles - Sedation Dentistry? | Los Gatos is far. Forget it, I'll call them myself. | (none) |  |  |  |  |  |
| 23 | SYN-0337 | Can you please confirm that you want me to book an appointment for you at 1512 Barber Shop on March 7th at 10:45 am. | Hmm, can we bump it to 11:15? | 11:15 = NEW_VALUE; bump = UPDATE_CUE |  |  |  |  |  |
| 24 | SYN-0362 | I'll book you a table for 4 at 2g Japanese Brasserie in San Francisco for March 1st at 7 pm. Is that correct? | All good, confirm it. | (none) |  |  |  |  |  |
| 25 | SYN-0397 | From the current forecast they have displayed, it looks like it will be 96 degrees Fahrenheit with a 5 percent chance of rain. | Yikes, and the week after? | the week after = NEW_VALUE |  |  |  |  |  |
| 26 | SYN-0403 | There are 10 Palo Alto options. Perhaps Abadi Esfandiar is a possibility for you. | Anyone who's a woman doctor in Palo Alto? | (none) |  |  |  |  |  |
| 27 | SYN-0457 | Kindly ensure that, play the song Windows Down on TV. | Ok but switch it to the patio speaker. | the patio speaker = NEW_VALUE; switch = UPDATE_CUE |  |  |  |  |  |
| 28 | SYN-0500 | I found 3 more you might like. One is Blue Jays Vs Orioles. It's at Rogers Centre next Wednesday at 6:30 pm | Orioles sounds great, 2 tickets. | Orioles = REFERENCE; 2 tickets = NEW_VALUE |  |  |  |  |  |
| 29 | SYN-0503 | Sure, there are 4 cars you might like, one of which is a Standard Civic available for pickup at Union Station on March 2nd. | Civic sounds fine, I'll take it. | Civic = REFERENCE |  |  |  |  |  |
| 30 | SYN-0507 | I searched and found 3 cars for you. A nice Compact Cooper car is available at Fresno Station on March 8th. | Cooper's cute. Do they have it on the 9th? | Cooper = REFERENCE; the 9th = NEW_VALUE |  |  |  |  |  |
| 31 | SYN-0573 | There are 4. What about a standard Accord on March 11th. Picking up at SMF International Airport . | Accord works, but pickup on the 12th. | Accord = REFERENCE; the 12th = NEW_VALUE |  |  |  |  |  |
| 32 | SYN-0639 | An Economy extra bus departs at 7:50 am and costs $44. | 7:50 works, 2 tickets please. | 7:50 = REFERENCE; 2 tickets = NEW_VALUE |  |  |  |  |  |
| 33 | SYN-0644 | Yup! The Courtyard Apartments located with good amenities at 1711 Detroit Avenue too have 4 bed rooms, 3 baths and the rent is just $4,700 per month. | Still a lot. Same number of rooms in Hayward? | Same number of rooms = REFERENCE; Hayward = NEW_VALUE |  |  |  |  |  |
| 34 | SYN-0666 | There is a bus leaving at 7 am for that route. An economy class ticket costs $29. | Too early. Is there one after lunch? | after lunch = NEW_VALUE |  |  |  |  |  |
| 35 | SYN-0700 | Please confirm the following: 1 economy ticket for a Delta Airlines flight from Chicago to London. It departs March 11th at 11:05 am and returns March 13th at 8 am. | Make it 2 tickets, same flight. | 2 tickets = NEW_VALUE; same flight = REFERENCE; Make it = UPDATE_CUE |  |  |  |  |  |
| 36 | SYN-0711 | Their rating is 3.8. Their phone number is 707-521-7760. I apologize that I was unable to book an appointment. What about Helena A. Longin, M.D. for March 6th at 12 pm? | Sure, Dr. Longin works. | Dr. Longin = REFERENCE |  |  |  |  |  |
| 37 | SYN-0754 | No problem. So do you want me to book the table for 3 on March 7th? | Yes, 3 on the 7th, same time. | 3 = NEW_VALUE; the 7th = REFERENCE; same time = REFERENCE |  |  |  |  |  |
| 38 | SYN-0785 | There's Celine Dion at Chase Center Experience for today at 6:30 pm. | Celine tonight? Yes! 2 tickets. | Celine = REFERENCE; tonight = REFERENCE; 2 tickets = NEW_VALUE |  |  |  |  |  |
| 39 | SYN-0802 | Melo's Pizza & Pasta Livermore serves pizza in Livermore. | Melo's works. Table for 2 at 6:30. | Melo's = REFERENCE; Table = NEW_VALUE; 2 = NEW_VALUE; 6:30 = NEW_VALUE |  |  |  |  |  |
| 40 | SYN-0852 | Dr. Donald R. Dossett, MD is a General Practitioner in South San Francisco. | Dr. Dossett is fine. Tuesday morning. | Dr. Dossett = REFERENCE; Tuesday morning = NEW_VALUE |  |  |  |  |  |
| 41 | SYN-0857 | I did find 1 that fits your desires that would be Ramen Shop. | Ramen Shop sounds cozy. Play it. | Ramen Shop = NEW_VALUE |  |  |  |  |  |
| 42 | SYN-0860 | Yes, found 1 and it is 1 Hotel Brooklyn Bridge with rating 4.5, how about it? | Brooklyn Bridge one, book it from the 6th. | Brooklyn Bridge one = REFERENCE; the 6th = NEW_VALUE |  |  |  |  |  |
| 43 | SYN-0877 | The average temperature for today is 89 degrees Farenheit and there is a 15 percent chance of rain. | Hot. And Flagstaff? | Flagstaff = NEW_VALUE |  |  |  |  |  |
| 44 | SYN-0892 | Please confirm that you want to play Lady Luck on the TV. | Correct, Lady Luck on TV. | Lady Luck = NEW_VALUE; TV = NEW_VALUE |  |  |  |  |  |
| 45 | SYN-0898 | Can you please confirm that you'd like 1 ticket to the event taking place on March 10th? | Yes, 1 ticket for the 10th. | 1 ticket = NEW_VALUE; the 10th = REFERENCE |  |  |  |  |  |
| 46 | SYN-0931 | I found a bus leaving at 8:30 am with 0 transfers. The ticket is $19. | Yes, that 8:30 bus, reserve 2 seats. | that 8:30 bus = REFERENCE; 2 seats = NEW_VALUE |  |  |  |  |  |
| 47 | SYN-0932 | how about alta eye care in san jose? They are actually an ophthalmologist | San Jose is far. Do they have an office in Campbell? | Campbell = NEW_VALUE |  |  |  |  |  |
| 48 | SYN-0948 | ABC Hyde Park Hotel has a rating of 3.2. | 3.2 is too low. Can we go back to the first hotel you found? | the first hotel you found = REFERENCE; go back to = RESTORE_CUE |  |  |  |  |  |
| 49 | SYN-0985 | Okay, sure. You want to get your hair done at Great Clips, starting at 2:15 pm on March 14th? | Oops, wrong salon. I wanted Supercuts, same time. | Supercuts = NEW_VALUE; same time = REFERENCE |  |  |  |  |  |
| 50 | SYN-0987 | confirm alegrias to san francisco at 6 pm and for 2 people on march 1st | Yes, and we're actually 3 people, not 2. | 3 people = NEW_VALUE; 2 = OLD_VALUE; actually = UPDATE_CUE |  |  |  |  |  |
