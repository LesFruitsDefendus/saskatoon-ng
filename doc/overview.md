# Saskatoon Overview

Saskatoon is a fruit harvest management system built for the Montreal-based urban fruit gleaning collective [Les Fruits Défendus](https://santropolroulant.org/en/what-is-the-roulant/collectives/fruits-defendus/). The initiative connects local fruit tree owners with volunteer harvesters and helps ensure that this valuable local food resource does not go to waste. After the fruit is harvested, it is usually divided among the tree owner, volunteers, and some beneficiary organizations.

The main functionalities can be divided into 2 categories:
- Record keeping
- Facilitating harvests

## Record Keeping

Saskatoon keeps several groups of records (*NOTE: this is only conceptual, not the actual database implementation*):

- **personnel**
    - *__tree owners__*: who offer fruit trees for harvest. Trees can be owned by an organization, e.g. McGill University.
    - *__pick-leaders__*: who lead individual harvests from start to end, i.e. organize and oversee picks, transport equipment to and from harvests, bring fruit to beneficiary organizations and log the day’s bounty in Saskatoon.
    - *__volunteers / harvesters__*: who help pick the fruits during a harvest. Record-keeping of harvesters can help pick-leaders assemble the harvest teams, e.g. offering more opportunities to first-time harvesters when the participation requests exceed the available spots.
    - *__core members / admins__*: who have full access to the system and records, and can grant/revoke access and permission.
- **properties / locations & fruit trees**: where and what to harvest. One property may have multiple types of fruit trees, and one type of fruit trees may have multiple harvests each year.
- **beneficiary organizations**: external recipients of fruits. A portion of the harvest can be donated to local communities.
- **harvests & participation requests**: Each harvest record contains various info, e.g. date & time, location, yield of each type of fruits, participants, how the fruits were distributed, etc.
- **equipments**: tools that pick leaders can borrow for harvests, e.g. ladders, bikes, scales, and etc.

## Facilitating harvests

### Pick-leader

Pick-leaders use the Saskatoon dashboard to organize harvests and log the results afterward. A series of activities would happen around the harvest record during a harvest.

| Stage                                                                                                                                                                                                                            | Status in harvest record | Time range in harvest record | Other info added in harvest record                |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------:|------------------------------|---------------------------------------------------|
| 1. A new harvest record for the current year is created in Saskatoon after the tree owner confirms the interest to participate this year. It usually happens before the season starts.                                           |         _Orphan_         | usually a 2-week period      | property and trees                                |
| 2. A pick-leader declares to lead this harvest                                                                                                                                                                                   |        _Adopted_         | same as previous             | pick-leader                                       |
| 3. The pick-leader confirms with the tree owner about the exact harvest date and time, contacts beneficiary organizations to receive fruits for this harvest, and publish the event on harvest calendar to call for participants |     _Date scheduled_     | A specific date and time     | beneficiary organizations, participation requests |
| 4. The pick-leader assembles the team for harvest by accepting/declining participation requests                                                                                                                                  |         _Ready_          | same as previous             | participation requests status updated             |
| 5. Harvest ends. If successful, the pick-leader logs the harvest yield and how the fruits were distributed among the tree owner, volunteers, and beneficiary organizations                                                       | _Successful / Cancelled_ | same as previous             | harvest yield and distribution info               |

### Volunteers / harvesters

Volunteers / harvesters use the Saskatoon public harvest calendar to browse harvest events. They can submit participation requests to 'open' events before their status is changed to _Ready_. 

### Core members / admins

Core members / admins use the Saskatoon dashboard and admin panel to manage personnel (e.g. grant access & permission for dashboard to new pick-leaders) and other records (e.g. delete duplicate properties).

## Other functionalities

- Statistics on harvest
- On-boarding materials and resources for pick-leaders
- Template-based auto email system for notification
- Multi-locale support and translation panel