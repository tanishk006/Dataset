DOCUMENT_COUNTS = {
    "7/12": 350,
    "8A": 150,
    "Property Card": 150,
    "Sale Deed": 200,
    "Mutation Document": 200,
    "Registration Document": 150,
    "Court Order": 150,
    "Death Certificate": 100,
    "Legal-Heir/Succession": 150,
    "Survey Document": 150,
    "Compensation Document": 100,
    "Award Document": 75,
    "Possession Document": 75,
    "R&R Document": 75,
    "Other": 125,
}

LANGUAGE_RATIOS = {
    "English": 0.45,
    "Marathi": 0.30,
    "Marathi-English": 0.25,
}

NOISE_RATIOS = {
    "Clean OCR": 0.35,
    "Formatting variation": 0.20,
    "OCR character noise": 0.15,
    "Missing fields": 0.10,
    "Low-quality scan": 0.10,
    "Marathi/English variation": 0.10,
}

# The specifications do not prescribe a conflict percentage.
# Keep it configurable and default to zero unless the project owner requests conflicts.
DEFAULT_CONFLICT_RATE = 0.0

# Pools are intentionally synthetic and should never be presented as government data.
FIRST_NAMES = [
    "Ramesh", "Sunita", "Amit", "Priya", "Vijay", "Kavita", "Sanjay", "Neha",
    "Mahesh", "Pooja", "Rahul", "Anita", "Nitin", "Meena", "Sachin", "Swati",
    "Deepak", "Madhuri", "Prakash", "Rekha", "Ajay", "Sneha", "Ganesh", "Asha",
]
LAST_NAMES = [
    "Patil", "Jadhav", "Shinde", "Deshmukh", "Pawar", "More", "Chavan",
    "Kadam", "Bhosale", "Gaikwad", "Kulkarni", "Joshi", "Sawant", "Mane",
]

LOCATIONS = [
    ("Satara", "Phaltan", "Suryapur"),
    ("Pune", "Baramati", "Mangalwadi"),
    ("Nashik", "Sinnar", "Deopur"),
    ("Kolhapur", "Karvir", "Shivajinagar"),
    ("Ahmednagar", "Rahata", "Sonwadi"),
    ("Solapur", "Malshiras", "Akluj"),
    ("Sangli", "Miraj", "Kupwad"),
    ("Nanded", "Loha", "Pimpalgaon"),
]

ISSUERS = [
    "Revenue Department", "Sub-Registrar Office", "Taluka Revenue Office",
    "District Land Records Office", "Civil Court", "Survey Department",
    "Compensation Authority", "Rehabilitation Office", "Local Registration Office",
]

STATUSES = [
    "Issued", "Pending", "Registered", "Verified", "Under Review",
    "Amended", "Transferred", "Closed", "Provisional", "Rejected",
]

MARATHI = {
    "land_record": "जमीन नोंद अभिलेख",
    "survey": "सर्वे क्रमांक",
    "subdivision": "उपविभाग",
    "holder": "धारक",
    "village": "गाव",
    "taluka": "तालुका",
    "district": "जिल्हा",
    "issue_date": "जारी दिनांक",
    "registration": "नोंदणी क्रमांक",
    "document": "दस्तऐवज क्रमांक",
    "date": "दिनांक",
    "seller": "विक्रेता",
    "buyer": "खरेदीदार",
    "mutation": "फेरफार",
    "order": "आदेश",
    "certificate": "प्रमाणपत्र",
    "status": "स्थिती",
    "issuer": "जारी करणारे कार्यालय",
}
