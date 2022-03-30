# Saskatoon user stories

Use this file to test all use cases Saskatoon is supposed to cover.

## Core member, user profile

### as a core member, I want to add a new person (as a pickleader I don't have access):

1. Visit the `Community` tab >> https://saskatoon-dev.lesfruitsdefendus.org/community/
2. Click on `+ New Person` >> https://saskatoon-dev.lesfruitsdefendus.org/person/create/
3. Make sure to select the appropriate role for the new member
4. Fill out the form and save
5. The person now appears in the community list.
6. Note that the newly created user doesn't have login credentials (i.e. cannot log into saskatoon)
7. If you now wish to register the user click on the `+` sign below their email address.
8. You are redirected to the admin panel to finalize the action
9. Enter a temporary password twice and click on `Change Password`
10. Save the user form
11. Communicate the password to the new user through secure means. They can now log in.
12. Leave the admin panel by clicking on `View Site` in the top right of the screen


### as a core member, I want to edit a person (as a pickleader I don't have access):
	
1. Visit the `Community` tab >> https://saskatoon-dev.lesfruitsdefendus.org/community/
2. Click on the blue pen next to the person's name
3. Edit and save the form


### as a core member, I want to delete a person (as a pickleader I don't have access):

1. Visit the `Community` tab >> https://saskatoon-dev.lesfruitsdefendus.org/community/
2. Click on the red trash can next to the person ID
3. A pop up will ask you to confirm, click OK
4. You are redirected to the admin panel to finalize the action
5. It is likely that the user deletion will cause other objects to be deleted (e.g. Harvests)
6. Review the list it carefully and click `Yes` only if you're sure
7. Leave the admin panel by clicking on `View Site` in the top right of the screen

### as a core member, I want to review a pending property :

1. Create a new pending property through the public form:  https://saskatoon-dev.lesfruitsdefendus.org/property/create_public/
2. After sending the form, the *Thank you* page might not load properly, it's a known issue.
3. Visit the `Properties` tab.
4. Click on the name of the pending property you just created.
5. Note it is labeled as `** PENDING **`. Click on `Edit Property`.
6. Review the information and uncheck the `pending` box before saving.
7. Now the property is no longer pending but it's owner still has to be registered

    Option A: the owner is already in the database (e.g. they sent a renewal form)
    - Click on `Edit Property` and search for a registered owner in the `Owner` dropdown menu
    - Save the form

    Option B: the owner submitted the form for the first time, it must be registered
    - Click on `register` next to the `Contact` header
    - Format the First and Last names properly

### as a core member, I want to validate a property and make it an orphan harvest for the season in course

### as a core member, I want to add to/edit the list of beneficiary organisations (as a pickleader I don't have access)

### as a core member, I want to add to/edit the list of equipment points (as a pickleader I don't have access)

### as a core member, I want to review annual statistics

## Pick Leader, user profile

### as a pick leader, I want to select a tree to harvest and schedule the harvest date publicly

### as a pick leader, I want to reserve the equipment from a certain point for the date of my harvest

### as a pick leader, I want to enter the harvest data after it is complete

### as a pick leader, I want to communicate with volunteers to confirm/deny participation

### as a pick leader, I want to communicate with other collective members in my neighborhood (make groups based on neighborhood, add neighborhood question to the form for new pick leader accounts ?) 
