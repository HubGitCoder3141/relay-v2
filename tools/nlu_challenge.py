"""Versioned synthetic challenge notices kept separate from training templates."""
from tools.nlu_data import annotate


ROSTER = ("Eli Cole", "Nora Vale", "Iris Bell", "Robin", "Luca", "Avery Chen")
EXAMPLES = (
    ("Fyi—<title>basketball scrimmage</> has a <time>6:15 PM</> tip-off <date>Friday</> at <location>Gym B</>. Pack <preparation>a light and a dark jersey</>.", "sports", "schedule"),
    ("For <person>Nora</>: <title>violin rehearsal</>, <date>Sunday</> / <time>09:30</>, <location>Studio 2</>.", "event", "schedule"),
    ("<person>Eli</> must upload <title>the fraction worksheet</> by <deadline>Thursday</>. <instructions>Use the link from the teacher</>.", "homework", "schedule"),
    ("Could <responsibility>Robin</> drive <person>Iris</> to her <title>orthodontist checkup</> <date>tomorrow</> at <time>10:40 AM</>?", "appointment", "schedule"),
    ("Our <title>block association meeting</> is in <location>the community room</> at <time>7 PM</> on <date>Monday</>.", "meeting", "schedule"),
    ("Next up for <person>Luca</>: <title>planetarium trip</> on <date>December 8, 2026</>. Bus departs <time>08:20</>. Pack <preparation>a lunch and a jacket</>.", "trip", "schedule"),
    ("<title>Library returns</> must be done by <deadline>Tuesday</>. <instructions>Put the books in the outside bin</>.", "reminder", "schedule"),
    ("<title>Band recital</> starts <date>December 9, 2026</> at <time>6 PM</>. <instructions>Arrive at <location>the stage door</> before 5:15</>.", "event", "schedule"),
    ("Instead of Friday, <title>tennis practice</> will now be <date>Saturday</> at <time>11 AM</> in <location>Court 3</>.", "sports", "update"),
    ("Quick change: <title>the family photo session</> is going ahead <date>Wednesday</>, <time>4 PM</>. Ignore Monday's reminder.", "event", "update"),
    ("<title>Book fair</> isn't happening today after all. We'll let you know when there is a new date.", "event", "cancel"),
    ("Please ignore the old invitation. The <title>parent council meeting</> will not take place on Tuesday.", "meeting", "cancel"),
    ("Piano recital on Friday, dog appointment on Saturday. Please add both.", "unknown", "multiple"),
    ("I can't find the time for the skating lesson. Has anyone heard from the rink yet?", "unknown", "none"),
    ("We went to the concert last Friday and had a wonderful time.", "unknown", "none"),
    ("The game might happen Tuesday if the rain clears. No decision yet.", "unknown", "none"),
    ("<responsibility>Avery</> can handle <title>bus pickup</> for <person>Luca</> at <location>the west gate</> <date>tomorrow</>.", "reminder", "schedule"),
    ("Please submit <title>the permission form</> by <deadline>Dec 1, 2026</> for <person>Nora</>. <instructions>Give it to the front office</>.", "homework", "schedule"),
    ("<title>School movie night</> opens at <time>5 PM</> on <date>December 11</>. Bring <preparation>a blanket</>.", "event", "schedule"),
    ("<person>Eli</>'s <title>archery lesson</> is on <date>Thursday</> at <time>4 PM</> in <location>Room 19</>.", "sports", "schedule"),
    ("<title>Orthopedic follow-up</> is postponed. Clinic will call us with a new day.", "appointment", "cancel"),
    ("The weekend trip might be rebooked, but nobody has confirmed a departure.", "unknown", "none"),
)
RELEASE = (
    ("For <person>Iris</>, <title>the skating lesson</> begins at <time>17:30</> on <date>Wednesday</> in <location>Rink 6</>. Bring <preparation>a helmet and gloves</>.", "sports", "schedule"),
    ("<title>Write up the lab observations</> by <deadline>Friday</> for <person>Eli</>. <instructions>Put the answers in the online notebook</>.", "homework", "schedule"),
    ("<title>A neighborhood planning meeting</> is at <location>the small lounge</> on <date>Tuesday</> at <time>7:45 PM</>.", "meeting", "schedule"),
    ("The clinic moved <title>the hearing test</> to <date>December 18, 2026</> at <time>14:00</> for <person>Nora</>.", "appointment", "update"),
    ("<responsibility>Robin</> is taking <person>Luca</> to <title>the passport appointment</> <date>tomorrow</> at <time>09:45</>. Pack <preparation>the old passport</>.", "appointment", "schedule"),
    ("<title>Uniform return</> is due <deadline>Monday</>. <instructions>Put it in the bag by the main door</>.", "reminder", "schedule"),
    ("About <title>our ferry outing</>: the boat leaves <date>Saturday</> at <time>06:50</>. <instructions>Wait at <location>Pier 2</> by 6:15</>.", "trip", "schedule"),
    ("We've changed <title>the talent show</> from next week to <date>December 6, 2026</> at <time>4 PM</>. The address is <location>West Campus</>.", "event", "update"),
    ("<title>Practice at the track</> is called off because of lightning. No replacement time has been announced.", "sports", "cancel"),
    ("<title>The nutrition class</> won't take place on Friday. We will send an update.", "event", "cancel"),
    ("If the rink is open, skating might happen this afternoon. We're waiting on confirmation.", "unknown", "none"),
    ("Any idea when the chorus rehearsal is? The newsletter doesn't have a date.", "unknown", "none"),
    ("Swim class Monday, pediatric checkup Friday. These are two different plans.", "unknown", "multiple"),
    ("Hi <person>Nora</> — <title>the painting workshop</> at <location>Studio 8</> is <date>Sunday</> at <time>10 AM</>. Bring <preparation>an old shirt</>.", "event", "schedule"),
)


def examples(release=False):
    return [annotate(text, kind, intent, ROSTER) for text, kind, intent in (RELEASE if release else EXAMPLES)]
