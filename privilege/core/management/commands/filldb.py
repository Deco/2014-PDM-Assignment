from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from core.models import *
from core.history import *
import random
from django.db import transaction

class Command(BaseCommand):
    args = ''
    help = 'stuff'
    
    def _fill_db(self):
        print "Filling database..."
        with transaction.commit_on_success():
            #userChoices.shuffle()
            random.shuffle(self.facultyChoices)
            random.shuffle(self.projectChoices)
            
            userList = []
            userCount = len(self.userChoices)
            for userI in range(userCount):
                choice = self.userChoices[userI]
                user = self._make_user(str(userI+1), choice[0], choice[1], choice[2], (userI == 0))
                userList.append(user)
                record_history(kind=HistoryEntry.USER_CREATED,
                    note="Created with staff ID: {0}".format(userI+1),
                    referenced_user_primary=userList[0],
                    referenced_user_secondary=user
                )
            
            print(userList)
            
            facultyList = []
            while len(self.projectChoices) > 0 and len(self.facultyChoices) > 0:
                randomUsers = random.sample(userList, random.randrange(5, 15+1))
                faculty = self._make_faculty(
                    self.facultyChoices.pop(),
                    zip(randomUsers, ['M', 'A', 'A', 'A', 'A', 'M', 'A', 'A', 'M', 'A', 'A', 'M', 'A', 'A', 'M', 'A', 'A', 'M'])
                )
                facultyList.append(faculty)
                
                projectCount = random.randrange(min(6, len(self.projectChoices)), min(11, len(self.projectChoices))+1)
                for projectI in range(projectCount):
                    randomUsers = random.sample(userList, random.randrange(8, 25))
                    self._make_project(
                        self.projectChoices.pop(),
                        faculty,
                        zip(randomUsers, ['P','M','R','C','R','C','M','R','C','M','R','C','R','C','M','R','C','M','R','C','R','C','M','R','C','M','R','C','R','C','M','R','C','M'])
                    )
    
    def _make_user(self, username, first_name, last_name, password, is_admin):
        print(username, first_name, last_name, password)
        return self._make(User,
            username=username,
            first_name=first_name, last_name=last_name,
            password=make_password(password),
            is_staff=is_admin, is_superuser=is_admin
        )
    
    def _make_faculty(self, name, members):
        faculty = self._make(Faculty,
            name=name
        )
        record_history(kind=HistoryEntry.FACULTY_CREATED,
            note='Name: "{0}"'.format(name),
            referenced_faculty=faculty,
            referenced_user_primary=members[0][0],
        )
        for pair in members:
            print("wtf", pair[0], pair[1])
            membership = self._make(FacultyMembership,
                faculty=faculty,
                member=pair[0],
                role=pair[1]
            )
            record_history(kind=HistoryEntry.FACULTY_MEMBER_ADDED,
                note='User "{0}" added as "{1}".'.format(membership.member, membership.get_role_nice()),
                referenced_faculty=faculty,
                referenced_user_primary=members[0][0],
                referenced_user_secondary=pair[0]
            )
        return faculty
    
    def _make_project(self, title, faculty, members):
        faculty = faculty #Faculty.objects.get(name__icontains=facultyName)
        capacity = random.randrange(0, 2014*10, 1)
        project = self._make(Project,
            title=title,
            faculty=faculty,
            storage_capacity_mb=capacity,
            storage_used_mb=random.randrange(0,capacity,1),
        )
        creator = FacultyMembership.objects.filter(faculty=faculty,role='M').order_by('?')[0].member
        record_history(kind=HistoryEntry.PROJECT_CREATED,
            note='Project created in faculty "{0}"'.format(faculty.name),
            referenced_faculty=faculty,
            referenced_project=project,
            referenced_user_primary=creator
        )
        is_first = True
        for pair in members:
            membership = self._make(ProjectMembership,
                project=project,
                member=pair[0],
                role=pair[1]
            )
            adder = (
                    is_first and creator
                or  ProjectMembership.objects.filter(project=project,role__in=['P','M']).order_by('?')[0].member
            )
            is_first = False
            record_history(kind=HistoryEntry.PROJECT_MEMBER_ADDED,
                note='User "{0}" added as "{1}".'.format(membership.member, membership.get_role_nice()),
                referenced_project=project,
                referenced_user_primary=adder,
                referenced_user_secondary=pair[0],
            )
        
        record_history(kind=HistoryEntry.PROJECT_EDITED,
            note='Changes: Title changed to "{0}";'.format(project.title),
            referenced_project=project,
            referenced_user_primary=creator,
        )
        return project
    
    def _make(self, kind, *args, **kwargs):
        obj = kind(*args, **kwargs)
        obj.save()
        return obj
    
    def handle(self, *args, **options):
        self._fill_db()
    
    userChoices = [
        ('Cornelius', 'Chase', 'password'),
        ('Dee', 'Doss', 'h4cker'),
        ('Mary', 'Poppins', 'penguins!'),
        ('Edward', 'Von Hamburger', 'aka jake'),
        ('Penny', 'Pound', 'PP'),
        ('Anisha', 'Ahner', 'AA'),
        ('Charlesetta', 'Chupp', 'CC'),
        ('Madaline', 'Mazzotta', 'MM'),
        ('Josephina', 'Jenkins', 'JJ'),
        ('Cathleen', 'Calton', 'CC'),
        ('Georgeann', 'Grundy', 'GG'),
        ('Manda', 'Mass', 'MM'),
        ('Avelina', 'Aragon', 'AA'),
        ('Edwardo', 'Eastham', 'EE'),
        ('Lynelle', 'Lerch', 'LL'),
        ('Galen', 'Gurganus', 'GG'),
        ('Lizabeth', 'Leveille', 'LL'),
        ('Dorotha', 'Dilley', 'DD'),
        ('Jina', 'Juneau', 'JJ'),
        ('Claudine', 'Cora', 'CC'),
        ('Harrison', 'Houde', 'HH'),
        ('Ladawn', 'Layton', 'LL'),
        ('Danyel', 'Deforest', 'DD'),
        ('Julienne', 'Jose', 'JJ'),
        ('Naida', 'Nelsen', 'NN'),
        ('Yen', 'Yzaguirre', 'YY'),
        ('Stephen', 'Shrader', 'SS'),
        ('Gail', 'Gryder', 'GG'),
        ('Romona', 'Rosenbloom', 'RR'),
        ('Carmel', 'Countess', 'CC'),
        ('Alecia', 'Abrahams', 'AA'),
        ('Phillis', 'Pichardo', 'PP'),
        ('Sabrina', 'Sowa', 'SS'),
        ('Berta', 'Bernier', 'BB'),
        ('Derek', 'Ditullio', 'DD'),
        ('Brittani', 'Baver', 'BB'),
        ('Tod', 'Tranmer', 'TT'),
        ('Jacqualine', 'Jarmon', 'JJ'),
        ('Lannie', 'Luckey', 'LL'),
        ('Pennie', 'Palazzo', 'PP'),
        ('Kellie', 'Koziol', 'KK'),
        ('Flavia', 'Friend', 'FF'),
        ('Juan', 'Jowett', 'JJ'),
        ('Nam', 'Nees', 'NN'),
        ('Sandra', 'Samford', 'SS'),
        ('Daphne', 'Doggett', 'DD'),
        ('Vannessa', 'Vandiver', 'VV'),
        ('Al', 'Aschenbrenner', 'AA'),
        ('Isis', 'Ivers', 'II'),
        ('Daren', 'Driskill', 'DD'),
        ('Royal', 'Ralls', 'RR'),
        ('Tammara', 'Talty', 'TT'),
        ('Oswaldo', 'Oakley', 'OO'),
        ('Catarina', 'Chaput', 'CC'),
    ]
    
    facultyChoices = [
        'Department of Science and Engineering',
        'Department of Computer Science',
        'Humanities International & Marketing Office (HIMO)',
        'Epidemiology and Biostatistics (School of Public Health)',
        'Department of Construction Management',
        'Curtin University Sustainability Policy (CUSP)',
        'Media, Culture and Creative Arts (School of)',
        'Education (School of)',
        'School of Management',
        'Business (Graduate School of)',
        'Film and Television (Screen Arts)',
        'School of Public Health',
        'Dietetics (School of Public Health)',
        'Vocational Training and Education Centre (VTEC)',
        'CBS (Curtin Business School)',
        'SMEC (Science and Mathematics Education Centre)',
        'Centre for Labour Market Research',
        'South Asia Research Unit',
        'School of Physiotherapy',
        'Office of the Vice-Chancellor',
        'Engineering (School of Mines)',
        'Architecture and Interior Architecture (Department of)',
        'School of Nursing and Midwifery',
        'Centre for International Health',
        'School of Public Health',
        'Geology (Department of Applied)',
        'MARG - Media Asia Research Group',
        'Spatial Sciences (Department of)',
        'NDRI (National Drug Research Institute)',
        'Faculty of Health Sciences',
        'Governance and Corporate Responsibility Research Unit',
        'Nanochemistry Research Institute (NRI)',
        'Statistics (Department of Mathematics and)',
        'Department of Urban and Regional Planning',
        'Sarawak Campus (Curtin)',
        'Education (School of)',
        'School of Built Environment',
        'Sydney Campus of Curtin University of Technology',
        'Business (Curtin Business School - CBS)',
        'School of Mines',
        'Vice-Chancellor\'s List',
        'Science and Engineering, Faculty of',
        'International Health (Centre for)',
        'School of Occupational Therapy and Social Work',
        'Handbook, Curtin Courses',
        'School of Accounting',
        'School of Psychology',
        'School of Civil and Mechanical Engineering',
        'Curtin Business School',
        'Centre for Aboriginal Studies',
        'Mining and Minerals Sciences and Engineering',
        'Department of Art',
        'Health (Centre for International)',
        'Aboriginal Studies (Centre for)',
        'Metallurgical and Minerals Engineering',
        'Vice-Chancellor (Office of the)',
        'Department of Dental Hygiene and Therapy',
        'School of Mines',
        'Petroleum Engineering (Department of)',
        'Department of Mechanical Engineering',
        'Design and Art (School of)',
        'Muresk Institute (Northam)',
        'School of Nursing and Midwifery',
        'Nursing & Midwifery (School of)',
        'Graduate School of Business',
        'Biomedical Sciences (School of)',
        'Centre for Labour Market Research',
        'Department of Social Sciences',
        'NDRI (National Drug Research Institute)',
        'School of Public Health',
        'PATREC - Planning and Transport Research Centre',
        'Environment and Agriculture (Department of)',
        'Marketing (School of)',
        'School of Occupational Therapy and Social Work',
        'Civil Engineering (Department of)',
        'Governance and Corporate Responsibility Research Unit',
        'Department of Human Biology',
        'Curtin Business School',
        'Nutrition (School of Public Health)',
        'Mechanical Engineering (Department of)',
        'Built Environment (School of)',
        'Internet Studies (Department of)',
        'Journalism (Department of)',
        'Institute of Theoretical Physics (ITP)',
    ]
    
    projectChoices = [
        'Self-determination theory and the facilitation of intrinsic motivation, social development, and well-being.',
        'Self-efficacy: Toward a unifying theory of behavioral change',
        'Users of the world, unite! The challenges and opportunities of Social Media',
        'The five competitive forces that shape strategy',
        'The theory of planned behavior.',
        'Theory of human motivation.',
        'Intrinsic and extrinsic motivations : Classic definitions and new directions',
        'Leading change: why transformation efforts fail',
        'Three approaches to qualitative content analysis',
        'The need to belong: desire for interpersonal attachments as a fundamental human motivation.',
        'The Truth about Fracking',
        'The rise of graphene',
        '3D printing: the dawn of a new era in manufacturing?',
        'Phytoremediation of Abandoned Crude Oil Contaminated Drill Sites of Assam with the Aid of a Hydrocarbon-Degrading Bacterial Formulation',
        'ZFN, TALEN, and CRISPR/Cas-based methods for genome engineering.',
        'Natural gas from shale formation - The evolution, evidences and challenges of shale gas revolution in United States',
        'CRISPR-Cas systems for editing, regulating and targeting genomes.',
        'Performance measurement system design: A literature review and research agenda',
        'Agricultural Biotechnology: Economics, Environment, Ethics, and the Future',
        'The Escalating Cost of College',
        'Judgment under uncertainty: Heuristics and biases',
        'Hallmarks of cancer: The next generation',
        'The framing of decisions and the psychology of choice',
        'Working memory',
        'Food security: the challenge of feeding 9 billion people',
        'Natural gas : Should fracking stop?',
        'Analysis of relative gene expression data using real-time quantitative PCR and the 2(T)(-Delta Delta C) method',
        'Induction of pluripotent stem cells from mouse embryonic and adult fibroblast cultures by defined factors',
        'Negotiated media effects. Peer feedback modifies effects of media\'s thin-body ideal on adolescent girls.',
        'Effects of biodiversity on ecosystem functioning: A consensus of current knowledge',
        'Three approaches to qualitative content analysis',
        'Autism',
        'Heart disease and stroke statistics--2013 update: a report from the American Heart Association.',
        'Google Scholar as replacement for systematic literature searches: good relative recall and precision are not enough.',
        'Political and Medical Views on Medical Marijuana and its Future',
        'Health Promotion by Social Cognitive Means',
        'Health benefits of physical activity: the evidence',
        'Eating disorders',
        'Prevalence of childhood and adult obesity in the United States, 2011-2012.',
        'The hospital anxiety and depression scale.',
        'Colour blindness in comptuing',
        'Explosions on the moon',
        'Adventures in underwater basketweaving',
        'Optimising the sensory characteristics and acceptance of canned cat food: use of a human taste panel.',
        'Effects of cocaine on honeybee dance behaviour.',
        'Swearing as a response to pain.',
        'Pigeons can discriminate "good" and "bad" paintings by children.',
        'The "booty call": a compromise between men\'s and women\'s ideal mating strategies.',
        'Intermittent access to beer promotes binge-like drinking in adolescent but not adult Wistar rats.',
        'Fellatio by fruit bats prolongs copulation time.',
        'More information than you ever wanted: does Facebook bring out the green-eyed monster of jealousy?',
        'Are full or empty beer bottles sturdier and does their fracture-threshold suffice to break the human skull?',
        'The nature of navel fluff.',
        'Parachute use to prevent death and major trauma related to gravitational challenge: systematic review of randomised controlled trials',
        'Consequences of Erudite Vernacular Utilized Irrespective of Necessity: Problems with Using Long Words Needlessly',
        'What is meow',
        'President Kennedy\'s death: A poison arrow-assisted homicide.',
        'Double feature: Personalities of punks and perils of their pointy parkas.',
        'Finally, a male contraceptive: behold the ball cozy!',
        'Bad news: you have a tumor. Good news: it\'s really cute!',
        'Times New Roman may be funnier than Arial, but why does Comic Sans make me want to kill myself?',
        'Nasal leech infestation: report of seven leeches and literature review.',
        'Did Gollum have schizophrenia or multiple personality disorder?',
        'Scientific analysis of Playboy centerfolds reveals Barbie-like vulvas.',
        'That\'s one miraculous conception.',
        'The Mere Anticipation of an Interaction with a Woman Can Impair Men\'s Cognitive Performance.',
        'Why overheard cell phone conversations are extra annoying.',
        'Cutting off the nose to save the penis.',
        'A scientific analysis of 400 YouTube videos of dogs chasing their tails.',
        'What did God do with Adam\'s penis bone?',
        'This study is soooo interesting.',
        'An unusual finding during screening colonoscopy: a cockroach!',
        'Mating competitors increase religious beliefs.',
        'A novel method for the removal of ear cerumen.',
        'Have a difficult problem to solve? Try vodka.',
        'That\'s one miraculous conception.',
        'An autopsy of chicken nuggets.',
        'Regardless of bladder size, all mammals pee for approximately 21 seconds.',
        'People prefer mates with a 22% resemblance to themselves.',
        'Foot orgasm syndrome. Yup, it\'s a thing.',
        'Trypophobia: fear of holes.',
        'Ever wanted to know what\'s really in hotdogs?',
        'Women\'s preference for male body hair changes across the menstrual cycle.',
        'Study proves "old person smell" is real.',
        'Does Guinness really taste better in Ireland? Science weighs in.',
        'Chemists explain why it\'s so hard to lift a wet glass from a table.',
        'Study finds that watching 3D movies makes 54.8% of people want to vomit.',
        'Mantis Shrimp\'s Bizarre Eyesight Finally Figured Out',
        'Why is butter sooooo delicious?',
        'Pleasure and pain: the effect of (almost) having an orgasm on genital and nongenital sensitivity.',
        'When the mafia does science.',
        'Visual cues given by humans are not sufficient for Asian Elephants (Elephas maximus) to find hidden food.',
        'Blow as well as pull: an innovative technique for dealing with a rectal foreign body.',
        'Phase 1: Build an army of remote-controlled turtles. Phase 2: ? Phase 3: Take over the world!',
        'Cunnilingus increases duration of copulation in the Indian flying fox.',
        'Powerful people are bigger hypocrites.',
        'If you feel like you can\'t work due to a hangover, you\'re probably right.',
        'Presenting the Meatball-French fries-Meatball-French fries-Meatball-French fries-Cream-Brownie-Cream-Brownie-Cream-Brownie diet!',
        '\'Beauty is in the eye of the beer holder\': People who think they are drunk also think they are attractive.',
        '20% of people who turn to the internet for sexual fulfillment leave dissatisfied.',
        'Is there a gene for self-employment?',
        'Left-handed people avoid using exact numbers.',
        'How long does roadkill linger on the pavement?',
        'Laughing rats are optimistic.',
        'The science of chick fights.',
        'Chimps in glasses...for science!',
        'Dying with laughter...literally.',
        'Dung beetles use the Milky Way for orientation.',
    ]
