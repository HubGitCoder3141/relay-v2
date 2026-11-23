"""Synthetic annotations for reproducible training, calibration, and held-out evaluation."""
from dataclasses import dataclass
import random
import re


@dataclass(frozen=True)
class Example:
    text: str
    kind: str
    intent: str
    spans: tuple
    members: tuple = ()


MARKUP = re.compile(r"<([a-z]+)>|</>")


def annotate(template, kind, intent, members=()):
    text, stack, spans = "", [], []
    last = 0
    for mark in MARKUP.finditer(template):
        text += template[last:mark.start()]
        if mark[1]:
            stack.append((mark[1], len(text)))
        else:
            field, start = stack.pop()
            spans.append((field, start, len(text)))
        last = mark.end()
    if stack:
        raise ValueError("Unclosed slot")
    return Example(text + template[last:], kind, intent, tuple(spans), members)


LEXICON = {
    "sports": ("soccer practice", "swim practice", "volleyball game", "track training"),
    "homework": ("history project", "math homework", "science assignment", "reading log"),
    "meeting": ("parent meeting", "budget meeting", "check-in meeting", "planning committee meeting"),
    "appointment": ("dentist appointment", "eye exam", "doctor visit", "physical therapy appointment"),
    "reminder": ("library book return", "medication reminder", "permission slip reminder", "trash pickup"),
    "trip": ("museum trip", "school field trip", "camping trip", "airport pickup"),
    "event": ("winter concert", "school play", "family dinner", "birthday party", "open house"),
    "person": ("Sam", "Morgan", "Charlie", "Jamie", "Maya Patel", "Chris", "Nico", "Riley", "Frances", "Ivan", "Lena", "Mika"),
    "responsibility": ("Alex", "Dana", "Tara", "Jordan Lee", "Priya", "Lee", "Ben", "Kim", "Drew", "Avery", "Harper", "Noor"),
    "contact": ("Coach Alex", "Ms. Lee", "Coach Dana", "the coordinator", "the team captain"),
    "date": ("Tuesday", "Wednesday", "Friday", "tomorrow", "today", "December 4", "2027-01-16", "Jan 8, 2027", "June 14, 2028", "Saturday", "November 26, 2027", "March 3"),
    "deadline": ("Monday", "Thursday", "tomorrow", "today", "December 2", "2027-01-15", "Jan 7, 2027", "Sunday", "April 17, 2028"),
    "time": ("5 PM", "7:30 a.m.", "16:15", "noon", "2 pm", "6:45 PM", "08:00", "4:30 p.m."),
    "arrival": ("4:45", "ten minutes early", "15:15", "8 AM", "6:15"),
    "location": ("the community field", "the school gym", "North Hall", "the library", "River Park", "Oak Medical Center", "the cafeteria", "classroom 204", "Court 7", "Room 23", "the drop-off lane", "the visitor entrance"),
    "bring": ("cleats and water", "a notebook", "the signed form", "a packed lunch", "a towel and goggles", "a pencil", "an insurance card"),
    "instruction": ("Enter through the east gate", "Use the side entrance", "Check in at the front desk", "Leave the bag by the door", "Wear the blue uniform", "Print the confirmation at home", "Upload it to the district portal", "Email the photo to the school office", "Use the link in the newsletter"),
}


FRAMES = (
    "{hello}<title>{title}</> is {place_on}<date>{date}</> at <time>{time}</>. Bring <preparation>{bring}</>. <instructions>Meet {contact} at <location>{location}</> by {arrival}</>.",
    "{hello}<person>{person}</> has <title>{title}</> on <date>{date}</> at <time>{time}</> in <location>{location}</>.",
    "For <person>{person}</>—<title>{title}</> starts at <time>{time}</> on <date>{date}</>. <instructions>{instruction}</>.",
    "Reminder: <title>{title}</>\nWhen: <date>{date}</>, <time>{time}</>\nWhere: <location>{location}</>\nWhat to bring: <preparation>{bring}</>",
    "Could <responsibility>{responsibility}</> handle <title>{title}</> for <person>{person}</> on <date>{date}</>? It begins at <time>{time}</>.",
    "<title>{title}</> on <date>{date}</> at <time>{time}</>. <instructions>Please check in at <location>{location}</> by {arrival}</>. Please RSVP by <deadline>{deadline}</>.",
    "Put <title>{title}</> on the calendar for <date>{date}</> at <time>{time}</>. <responsibility>{responsibility}</> will take <person>{person}</>.",
    "{hello}Please get <person>{person}</> ready for <title>{title}</>. It is on <date>{date}</> at <time>{time}</>. Pack <preparation>{bring}</>.",
    "Subject: <title>{title}</>\nFor: <person>{person}</>\nDeadline: <deadline>{deadline}</>\nResponsible: <responsibility>{responsibility}</>\nInstructions: <instructions>{instruction}</>",
    "The plan is <title>{title}</> at <location>{location}</> on <date>{date}</>. Start time is <time>{time}</>. Bring <preparation>{bring}</>.",
    "For <person>{person}</>, please submit <title>{title}</> by <deadline>{deadline}</>. <responsibility>{responsibility}</> will help. <instructions>{instruction}</>.",
    "On <date>{date}</>, there is <title>{title}</> for <person>{person}</>. The location is <location>{location}</>.",
    "<title>{title}</> will run from <time>{time}</> until {arrival} on <date>{date}</> at <location>{location}</>.",
    "<responsibility>{responsibility}</> is responsible for <title>{title}</>. <instructions>Have <person>{person}</> meet {contact} at <location>{location}</></> on <date>{date}</>.",
    "{hello}Our <title>{title}</> is scheduled at <location>{location}</> on <date>{date}</>. Doors open at {arrival}; the actual start is <time>{time}</>.",
    "<title>{title}</> {begin} at <time>{time}</> {day_link}<date>{date}</> in <location>{location}</>. <instructions>{instruction}</>.",
    "Could you ask <responsibility>{responsibility}</> to {take} <person>{person}</> to the <title>{title}</> <date>{date}</> at <time>{time}</>?",
    "<person>{person}</> is going to the <title>{title}</> on <date>{date}</>. <responsibility>{responsibility}</> will drive. <instructions>Meet in <location>{location}</> by {arrival}</>.",
    "{hello}We have the <title>{title}</> this week. <instructions>Meet in <location>{location}</> before {arrival}</>; the event starts at <time>{time}</> <date>{date}</>.",
    "<title>{title}</> {begin} at <time>{time}</> <date>{date}</>. <instructions>Arrive at <location>{location}</> by {arrival}</>.",
)
DUE_FRAMES = (
    "<person>{person}</> needs to {submit} <title>{title}</> by <deadline>{deadline}</>. <instructions>{instruction}</>.",
    "A reminder that <title>{title}</> is due <deadline>{deadline}</>. Bring <preparation>{bring}</>.",
    "For <person>{person}</>: <title>{title}</> has to be turned in by <deadline>{deadline}</>. <instructions>{instruction}</>.",
    "<responsibility>{responsibility}</> will help <person>{person}</> finish <title>{title}</> before <deadline>{deadline}</>.",
    "Don't forget <person>{person}</>'s <title>{title}</>. It needs to be done by <deadline>{deadline}</>.",
)
UPDATES = (
    "Update: <title>{title}</> moved from {deadline} to <date>{date}</>. New start time: <time>{time}</>. Same place.",
    "Change of plans: <title>{title}</> is now <date>{date}</> at <time>{time}</>, instead of {arrival}.",
    "Please move <title>{title}</> to <date>{date}</>. Use <location>{location}</> this time.",
    "{hello}<title>{title}</> has been moved to <date>{date}</> at <time>{time}</>. Ignore the previous time of {arrival}.",
    "<title>{title}</> changed: <date>{date}</> at <time>{time}</> in <location>{location}</>.",
)
CANCELLATIONS = (
    "{hello}<title>{title}</> is canceled. The old schedule was {date} at {time}.",
    "Cancel <title>{title}</> for {person}. We will reschedule later.",
    "There is no <title>{title}</> on {date}; it has been called off.",
    "<title>{title}</> was called off. Please do not go to {location} at {time}.",
    "Bad news: they have canceled <title>{title}</>. Don't show up on {date}.",
)
OTHER = (
    ("{person} says thank you! The photo turned out really well.", "none"),
    ("Can you confirm what we discussed? I don’t have the details yet.", "none"),
    ("We might do something if the weather holds. I will send the details later.", "none"),
    ("{title} is {date} at {time}, and {second} is {deadline} at {arrival}.", "multiple"),
    ("Two events this week: {title} at {location} and {second} in the gym.", "multiple"),
    ("There’s {title} on {date} and there’s {second} on {deadline}. They are separate.", "multiple"),
    ("We have {title} on {date}. Also, {second} on {deadline}.", "multiple"),
    ("I saw the notice about {title}, but I don’t know if it is going ahead.", "none"),
    ("Does anyone know when {title} is? I couldn't find a time.", "none"),
    ("{title} was fun! Thanks for getting {person} there yesterday.", "none"),
)

CALIBRATION = (
    ("Just a heads-up: <title>lacrosse practice</> will start at <time>5:20 PM</> on <date>Thursday</>. Pack <preparation>a helmet</>.", "sports", "schedule"),
    ("Please turn in <title>the geography worksheet</> by <deadline>Wednesday</>.", "homework", "schedule"),
    ("The <title>committee meeting</> for <person>Jules</> is at <location>City Hall</> <date>tomorrow</>.", "meeting", "schedule"),
    ("Could <responsibility>Olivia</> take <person>Jules</> to the <title>dentist appointment</> at <time>10 AM</> on <date>Tuesday</>?", "appointment", "schedule"),
    ("New date for <title>the aquarium trip</>: <date>Friday</>. The bus leaves at <time>8 AM</>.", "trip", "update"),
    ("A quick reminder to do the <title>library return</> by <deadline>Friday</>.", "reminder", "schedule"),
    ("<title>Graduation ceremony</> is canceled; please disregard the notice.", "event", "cancel"),
    ("The concert and the bike ride are both this weekend, at different locations.", "unknown", "multiple"),
    ("Thanks for sending the photos!", "unknown", "none"),
)

TEST = (
    ("Hey, <title>soccer practice</> is <date>Tuesday</> at <time>5 PM</>. Bring <preparation>cleats and water</>. <instructions>Meet Coach Alex at <location>the community field</> by 4:45</>.", "sports", "schedule"),
    ("<person>Amelia</> needs to submit <title>her science assignment</> by <deadline>Thursday</>. <instructions>Upload it to the school portal</>.", "homework", "schedule"),
    ("Our <title>parent meeting</> kicks off at <time>7 PM</> on <date>Friday</> in <location>Room 12</>.", "meeting", "schedule"),
    ("Please have <responsibility>Jules</> drive <person>Amelia</> to her <title>eye exam</> on <date>Monday</> at <time>2 PM</>.", "appointment", "schedule"),
    ("Quick reminder—<title>library book return</> is due <deadline>Wednesday</>. Bring <preparation>the library card</>.", "reminder", "schedule"),
    ("The <title>zoo trip</> leaves at <time>8:00 AM</> <date>tomorrow</>. <instructions>Meet in <location>the bus lot</> by 7:45</>.", "trip", "schedule"),
    ("<title>Spring concert</> moved to <date>May 15, 2027</> at <time>6:30 PM</>.", "event", "update"),
    ("<title>Softball practice</> has been called off. Don't go to the field tonight.", "sports", "cancel"),
    ("There’s soccer on Friday and a choir concert on Saturday. I will send both addresses separately.", "unknown", "multiple"),
    ("I got the sign-up info, but I don’t know whether the event is happening yet.", "unknown", "none"),
)


def training_examples(seed=41, per_frame=24):
    randomizer = random.Random(seed)
    rows = []
    kinds = tuple(LEXICON)[:7]

    def values(kind):
        return {**{key: randomizer.choice(options) for key, options in LEXICON.items()},
                "title": randomizer.choice(LEXICON[kind]),
                "second": randomizer.choice(LEXICON[randomizer.choice([k for k in kinds if k != kind])]),
                "hello": randomizer.choice(("", "Hey, ", "Hi all! ", "FYI, ", "Heads up: ")),
                "place_on": randomizer.choice(("", "on ")),
                "day_link": randomizer.choice(("", "on ")),
                "begin": randomizer.choice(("begins", "starts", "will start", "is starting", "is set to start")),
                "take": randomizer.choice(("drive", "bring", "take", "escort")),
                "submit": randomizer.choice(("submit", "turn in", "finish", "return"))}

    for kind in kinds:
        scheduled = FRAMES + (DUE_FRAMES if kind in ("homework", "reminder") else ())
        for frames, intent in ((scheduled, "schedule"), (UPDATES, "update"), (CANCELLATIONS, "cancel")):
            for frame in frames:
                for _ in range(per_frame):
                    sample = values(kind)
                    roster = (sample["person"], sample["responsibility"], "Taylor", "Quinn")
                    if randomizer.random() < .15:
                        roster = ()
                    rows.append(annotate(frame.format(**sample), kind, intent, roster))
    for frame, intent in OTHER:
        for _ in range(per_frame * len(kinds)):
            rows.append(annotate(frame.format(**values(randomizer.choice(kinds))), "unknown", intent))
    rows = list(dict.fromkeys(rows))
    randomizer.shuffle(rows)
    return rows


def evaluation_examples(split):
    roster = ("Jules", "Olivia", "Hugo", "Amelia", "Max", "Zoe")
    return [annotate(*row, roster) for row in (CALIBRATION if split == "calibration" else TEST)]
