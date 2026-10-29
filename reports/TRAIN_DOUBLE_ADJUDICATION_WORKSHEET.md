# Train/Dev Double-Set Adjudication Worksheet (6 disagreements / 60 double items)

**Rules:** C1 boundary / C2 value-ness / C3 deixis (guideline v0.2.2).
**Fill:** `KARAR:` satirina A, B veya OZEL + kisa gerekce. (Sadece iki hakem; etiket onerisi yok.)
*(Pilot-30 kararlari ayrica: reports/D3_ADJUDICATION_WORKSHEET.md)*

## 1. `SGD-835ec70f9e0a905054`
> Sounds good to me. Now get back to the restaurant. I'd like to book a table for three.

- A (Burak): NEW_VALUE "a table for three" [68-85]
- B (Enes): NEW_VALUE "a table" [68-75] | NEW_VALUE "three" [80-85]
- **KARAR:** `` — GEREKCE: 

## 2. `SGD-4dfe44204b3234df58`
> I need to head back to Chicago on the 9th so I plan to leave around 8 in the night.

- A (Burak): NEW_VALUE "the 9th" [34-41] | NEW_VALUE "8 in the night" [68-82]
- B (Enes): NEW_VALUE "the 9th" [34-41] | NEW_VALUE "around 8 in the night" [61-82]
- **KARAR:** `` — GEREKCE: 

## 3. `SGD-c5bd6a91af5fa668c3`
> cool, now let's go back to the restaurant thing, book a table for four at 1:15 pm

- A (Burak): NEW_VALUE "a table for four" [54-70] | NEW_VALUE "1:15 pm" [74-81]
- B (Enes): NEW_VALUE "a table" [54-61] | NEW_VALUE "four" [66-70] | NEW_VALUE "1:15 pm" [74-81]
- **KARAR:** `` — GEREKCE: 

## 4. `SGD-32ffc7799423754ec9`
> Alright, nice. Back to the bus tickets, I'll need tickets for four people.

- A (Burak): NEW_VALUE "tickets for four people" [50-73]
- B (Enes): NEW_VALUE "four people" [62-73]
- **KARAR:** `` — GEREKCE: 

## 5. `SGD-148b0aee03a8931e50`
> Okay. Now book an appointment at the salon n the same day at 11:15 in the morning

- A (Burak): NEW_VALUE "the salon" [33-42] | REFERENCE "the same day" [45-57] | NEW_VALUE "11:15 in the morning" [61-81]
- B (Enes): NEW_VALUE "an appointment" [15-29] | NEW_VALUE "the salon" [33-42] | REFERENCE "the same day" [45-57] | NEW_VALUE "11:15 in the morning" [61-81]
- **KARAR:** `` — GEREKCE: 

## 6. `SGD-9c4e5c1ad86443d8f3`
> That's great. I also want to book a dentist appointment on the same day.

- A (Burak): NEW_VALUE "a dentist appointment" [34-55] | KEPT_VALUE "the same day" [59-71]
- B (Enes): NEW_VALUE "a dentist appointment" [34-55] | REFERENCE "the same day" [59-71]
- **KARAR:** `` — GEREKCE: 
