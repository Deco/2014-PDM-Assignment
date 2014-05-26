from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from core.models import *
import random
from django.db import transaction

class Command(BaseCommand):
    args = ''
    help = 'stuff'
    
    def _fill_db(self):
        with transaction.commit_on_success():
            #userChoices.shuffle()
            random.shuffle(self.facultyChoices)
            random.shuffle(self.projectChoices)
            
            userList = []
            userCount = len(self.userChoices)
            for userI in range(userCount):
                choice = self.userChoices[userI]
                userList.append(
                    self._make_user(str(userI), choice[0], choice[1], choice[2], (userCount == 0))
                )
            
            print(userList)
            
            facultyList = []
            facultyCount = 8 #len(self.facultyChoices)
            projectsPerFacultyCount = 7
            for facultyI in range(facultyCount):
                randomUsers = random.sample(userList, random.randrange(1, 6))
                print(zip(randomUsers, ['M', 'A', 'A', 'A', 'A', 'M']))
                faculty = self._make_faculty(
                    self.facultyChoices[facultyI],
                    zip(randomUsers, ['M', 'A', 'A', 'A', 'A', 'M'])
                )
                facultyList.append(faculty)
                
                for projectI in range(projectsPerFacultyCount):
                    randomUsers = random.sample(userList, random.randrange(2, 10))
                    self._make_project(
                        self.projectChoices.pop(), #title
                        faculty,
                        zip(randomUsers, ['P','M','R','C','R','C','M','R','C','M'])
                    )


    def _make_user(self, username, first_name, last_name, password, is_admin):
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
        for pair in members:
            print("wtf", pair[0], pair[1])
            self._make(FacultyMembership,
                faculty=faculty,
                member=User.objects.get(username=pair[0]),
                role=pair[1]
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
        for pair in members:
            self._make(ProjectMembership,
                project=project,
                member=User.objects.get(username=pair[0]),
                role=pair[1]
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
    ]