"""
Scout Non-Tech Client Discovery & Intelligence Engine
Targets real decision makers with non-tech backgrounds (Founders, Owners, Managing Directors, CEOs)
across high-ticket industries: D2C Brands, Real Estate, Healthcare/Clinics, B2B Exporters, and Hospitality.
"""

import csv
import time
import os
import re
import argparse
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.table import Table
from rich import box

from app.memory import AgencyMemory, LeadMatcher
from app.scrapers.enrichment import LeadEnricher
from app.scrapers.tech_sniffer import TechSniffer
from app.scrapers.whatsapp_dispatcher import WhatsAppDispatcher

console = Console()

# Curated High-Value Non-Tech Target Client Directory
NON_TECH_CLIENTS = [
    # =========================================================================
    # INDIA (Founders, Owners, MDs of D2C, Real Estate, Clinics, B2B)
    # =========================================================================
    # --- D2C & E-Commerce Brands ---
    {"company": "Mokobara", "decision_maker": "Sangeet Agrawal", "role": "Founder & CEO", "niche": "d2c", "region": "India", "website": "https://mokobara.com", "industry": "D2C Travel & Luggage"},
    {"company": "Snitch", "decision_maker": "Siddharth Dungarwal", "role": "Founder", "niche": "d2c", "region": "India", "website": "https://snitch.co.in", "industry": "D2C Men's Fashion"},
    {"company": "Bare Anatomy", "decision_maker": "Rohit Chawla", "role": "Founder & CEO", "niche": "d2c", "region": "India", "website": "https://bareanatomy.in", "industry": "D2C Personal Care"},
    {"company": "BlueStone", "decision_maker": "Gaurav Singh Kushwaha", "role": "Founder & CEO", "niche": "d2c", "region": "India", "website": "https://bluestone.com", "industry": "Fine Jewellery"},
    {"company": "Heads Up For Tails", "decision_maker": "Rashi Narang", "role": "Founder", "niche": "d2c", "region": "India", "website": "https://headsupfortails.com", "industry": "Pet Care & Lifestyle"},
    {"company": "The Souled Store", "decision_maker": "Vedang Patel", "role": "Co-Founder & CEO", "niche": "d2c", "region": "India", "website": "https://thesouledstore.com", "industry": "Apparel & Merchandising"},
    {"company": "Sugar Cosmetics", "decision_maker": "Vineeta Singh", "role": "Co-Founder & CEO", "niche": "d2c", "region": "India", "website": "https://sugarcosmetics.com", "industry": "Beauty & Cosmetics"},
    {"company": "Plum Goodness", "decision_maker": "Shankar Prasad", "role": "Founder & CEO", "niche": "d2c", "region": "India", "website": "https://plumgoodness.com", "industry": "Clean Skincare"},
    {"company": "Mamaearth", "decision_maker": "Varun Alagh", "role": "Co-Founder & CEO", "niche": "d2c", "region": "India", "website": "https://mamaearth.in", "industry": "Toxin-Free Beauty"},
    {"company": "Country Delight", "decision_maker": "Chakradhar Gade", "role": "Co-Founder & CEO", "niche": "d2c", "region": "India", "website": "https://countrydelight.in", "industry": "Farm-Fresh Dairy"},
    {"company": "Sleepy Owl Coffee", "decision_maker": "Ajai Thandi", "role": "Co-Founder", "niche": "d2c", "region": "India", "website": "https://sleepyowl.co", "industry": "Specialty Coffee"},
    {"company": "Phool", "decision_maker": "Ankit Agarwal", "role": "Founder", "niche": "d2c", "region": "India", "website": "https://phool.co", "industry": "Sustainable Wellness"},
    {"company": "Bombay Shaving Company", "decision_maker": "Shantanu Deshpande", "role": "Founder & CEO", "niche": "d2c", "region": "India", "website": "https://bombayshavingcompany.com", "industry": "Men's Grooming"},
    {"company": "BoAt Lifestyle", "decision_maker": "Aman Gupta", "role": "Co-Founder & CMO", "niche": "d2c", "region": "India", "website": "https://boat-lifestyle.com", "industry": "Consumer Tech & Audio"},
    {"company": "Noise", "decision_maker": "Amit Khatri", "role": "Co-Founder", "niche": "d2c", "region": "India", "website": "https://gonoise.com", "industry": "Smart Wearables"},
    {"company": "Be Minimalist", "decision_maker": "Mohit Yadav", "role": "Founder", "niche": "d2c", "region": "India", "website": "https://beminimalist.co", "industry": "Active Skincare"},
    {"company": "WOW Skin Science", "decision_maker": "Manish Chowdhary", "role": "Co-Founder", "niche": "d2c", "region": "India", "website": "https://buywow.in", "industry": "Natural Personal Care"},
    {"company": "Licious", "decision_maker": "Abhay Hanjura", "role": "Co-Founder", "niche": "d2c", "region": "India", "website": "https://licious.in", "industry": "Fresh Meat & Seafood"},
    {"company": "Epigamia", "decision_maker": "Rohan Mirchandani", "role": "Co-Founder & CEO", "niche": "d2c", "region": "India", "website": "https://epigamia.com", "industry": "Premium Dairy & Greek Yogurt"},
    {"company": "Chaayos", "decision_maker": "Nitin Saluja", "role": "Founder", "niche": "d2c", "region": "India", "website": "https://chaayos.com", "industry": "Cafe Chain & Packaged Goods"},
    {"company": "Forest Essentials", "decision_maker": "Mira Kulkarni", "role": "Founder & MD", "niche": "d2c", "region": "India", "website": "https://forestessentialsindia.com", "industry": "Luxury Ayurvedic Beauty"},
    {"company": "Kapiva", "decision_maker": "Ameve Sharma", "role": "Founder", "niche": "d2c", "region": "India", "website": "https://kapiva.in", "industry": "Ayurvedic Nutrition"},
    {"company": "Dot & Key", "decision_maker": "Suyash Saraf", "role": "Co-Founder", "niche": "d2c", "region": "India", "website": "https://dotandkey.com", "industry": "Skincare & Cosmetics"},
    {"company": "mCaffeine", "decision_maker": "Tarun Sharma", "role": "Co-Founder & CEO", "niche": "d2c", "region": "India", "website": "https://mcaffeine.com", "industry": "Caffeinated Personal Care"},
    {"company": "Bella Vita Luxury", "decision_maker": "Aakash Anand", "role": "Founder", "niche": "d2c", "region": "India", "website": "https://bellavitaorganic.com", "industry": "Luxury Fragrances"},

    # --- Real Estate & Luxury Builders ---
    {"company": "Lodha Group", "decision_maker": "Abhishek Lodha", "role": "Managing Director", "niche": "real-estate", "region": "India", "website": "https://lodhagroup.in", "industry": "Luxury Residential & Commercial"},
    {"company": "Oberoi Realty", "decision_maker": "Vikas Oberoi", "role": "Chairman & MD", "niche": "real-estate", "region": "India", "website": "https://oberoirealty.com", "industry": "High-End Real Estate"},
    {"company": "Godrej Properties", "decision_maker": "Pirojsha Godrej", "role": "Executive Chairman", "niche": "real-estate", "region": "India", "website": "https://godrejproperties.com", "industry": "Premium Residential Developments"},
    {"company": "DLF Luxury", "decision_maker": "Rajiv Singh", "role": "Chairman", "niche": "real-estate", "region": "India", "website": "https://dlf.in", "industry": "Luxury Residences & Golf Estates"},
    {"company": "Hiranandani Group", "decision_maker": "Niranjan Hiranandani", "role": "Managing Director", "niche": "real-estate", "region": "India", "website": "https://hiranandani.com", "industry": "Integrated Luxury Townships"},
    {"company": "Prestige Group", "decision_maker": "Irfan Razack", "role": "Chairman & MD", "niche": "real-estate", "region": "India", "website": "https://prestigeconstructions.com", "industry": "Residential & Hospitality Developments"},
    {"company": "Sobha Limited", "decision_maker": "Ravi PNC Menon", "role": "Chairman", "niche": "real-estate", "region": "India", "website": "https://sobha.com", "industry": "Luxury Residences"},
    {"company": "Brigade Group", "decision_maker": "Pavitra Shankar", "role": "Managing Director", "niche": "real-estate", "region": "India", "website": "https://brigadegroup.com", "industry": "Real Estate Development"},
    {"company": "Piramal Realty", "decision_maker": "Anand Piramal", "role": "Executive Director", "niche": "real-estate", "region": "India", "website": "https://piramalrealty.com", "industry": "Ultra-Luxury Waterfront Living"},
    {"company": "Kolte-Patil Developers", "decision_maker": "Rajesh Patil", "role": "Chairman & MD", "niche": "real-estate", "region": "India", "website": "https://koltepatil.com", "industry": "Urban Luxury Developments"},

    # --- Healthcare, Clinics & Wellness ---
    {"company": "Clove Dental", "decision_maker": "Amarinder Singh", "role": "Founder & CEO", "niche": "healthcare", "region": "India", "website": "https://clovedental.in", "industry": "Dental Clinic Chain"},
    {"company": "Pristyn Care", "decision_maker": "Harsimarbir Singh", "role": "Co-Founder", "niche": "healthcare", "region": "India", "website": "https://pristyncare.com", "industry": "Advanced Surgical Centers"},
    {"company": "Kaya Skin Clinic", "decision_maker": "Rajiv Nair", "role": "Group CEO", "niche": "healthcare", "region": "India", "website": "https://kaya.in", "industry": "Aesthetic Dermatology Clinics"},
    {"company": "Oliva Clinic", "decision_maker": "Dr. Prashant Soma", "role": "Founder & CEO", "niche": "healthcare", "region": "India", "website": "https://olivaclinic.com", "industry": "Medico-Aesthetic Dermatology"},
    {"company": "Apollo Dental", "decision_maker": "Neeraj Garg", "role": "CEO", "niche": "healthcare", "region": "India", "website": "https://apollodental.in", "industry": "Dental Clinics Network"},
    {"company": "Dr Batra's", "decision_maker": "Dr. Mukesh Batra", "role": "Founder & Chairman", "niche": "healthcare", "region": "India", "website": "https://drbatras.com", "industry": "Holistic Healthcare Clinics"},
    {"company": "Indira IVF", "decision_maker": "Dr. Ajay Murdia", "role": "Founder & Chairman", "niche": "healthcare", "region": "India", "website": "https://indiraivf.com", "industry": "Fertility & IVF Specialty Clinics"},
    {"company": "Dentzz Dental", "decision_maker": "Dr. Shantanu Jaradi", "role": "Founder & Director", "niche": "healthcare", "region": "India", "website": "https://dentzz.com", "industry": "Cosmetic & Implant Dentistry"},

    # --- B2B, Manufacturing & Export ---
    {"company": "Arvind Limited", "decision_maker": "Sanjay Lalbhai", "role": "Chairman & MD", "niche": "b2b", "region": "India", "website": "https://arvind.com", "industry": "Textiles & Advanced Materials Export"},
    {"company": "Welspun Living", "decision_maker": "Dipali Goenka", "role": "CEO & MD", "niche": "b2b", "region": "India", "website": "https://welspunliving.com", "industry": "Home Textiles Global Exporter"},
    {"company": "Vardhman Textiles", "decision_maker": "Suchita Oswal Jain", "role": "Vice Chairperson & Joint MD", "niche": "b2b", "region": "India", "website": "https://vardhman.com", "industry": "Yarns & Fabric Manufacturing"},
    {"company": "Trident Group", "decision_maker": "Rajinder Gupta", "role": "Chairman Emeritus", "niche": "b2b", "region": "India", "website": "https://tridentindia.com", "industry": "Textiles & Paper Manufacturing"},
    {"company": "Raymond", "decision_maker": "Gautam Singhania", "role": "Chairman & MD", "niche": "b2b", "region": "India", "website": "https://raymond.in", "industry": "Textiles & Suiting Retail"},

    # =========================================================================
    # PAKISTAN (Founders, Owners, MDs of Retail, Fashion, Clinics, Export)
    # =========================================================================
    # --- Fashion & D2C Brands ---
    {"company": "Nishat Linen", "decision_maker": "Naz Mansha", "role": "Managing Director", "niche": "d2c", "region": "Pakistan", "website": "https://nishatlinen.com", "industry": "Fashion Apparel & Home Linen"},
    {"company": "Khaadi", "decision_maker": "Shamoon Sultan", "role": "Founder & CEO", "niche": "d2c", "region": "Pakistan", "website": "https://pk.khaadi.com", "industry": "Retail & Fashion Lifestyle"},
    {"company": "Sapphire Retail", "decision_maker": "Nabeel Abdullah", "role": "Director", "niche": "d2c", "region": "Pakistan", "website": "https://pk.sapphireonline.com.pk", "industry": "Designer Pret & Retail"},
    {"company": "Junaid Jamshed", "decision_maker": "Sohail Hamid Khan", "role": "Managing Director", "niche": "d2c", "region": "Pakistan", "website": "https://junaidjamshed.com", "industry": "Eastern Wear & Fragrances"},
    {"company": "Gul Ahmed", "decision_maker": "Ziad Bashir", "role": "Executive Director", "niche": "d2c", "region": "Pakistan", "website": "https://gulahmedshop.com", "industry": "Textiles & Retail Brand"},
    {"company": "Alkaram Studio", "decision_maker": "Fawad Anwar", "role": "Managing Director", "niche": "d2c", "region": "Pakistan", "website": "https://alkaramstudio.com", "industry": "Fashion Fabrics & Ready-to-Wear"},
    {"company": "Maria.B", "decision_maker": "Maria Butt", "role": "Founder & Creative Director", "niche": "d2c", "region": "Pakistan", "website": "https://mariab.pk", "industry": "Luxury Pret & Couture"},
    {"company": "Sana Safinaz", "decision_maker": "Sana Hashwani", "role": "Co-Founder", "niche": "d2c", "region": "Pakistan", "website": "https://sanasafinaz.com", "industry": "High-End Designer Pret"},
    {"company": "Bareeze", "decision_maker": "Hamid Zaman", "role": "Managing Director", "niche": "d2c", "region": "Pakistan", "website": "https://bareeze.com", "industry": "Embroidered Luxury Fabrics"},
    {"company": "Outfitters", "decision_maker": "Kamran Khurshid", "role": "Founder & CEO", "niche": "d2c", "region": "Pakistan", "website": "https://outfitters.com.pk", "industry": "Urban Fashion Chain"},
    {"company": "Charcoal", "decision_maker": "Muhammad Yousuf", "role": "Director", "niche": "d2c", "region": "Pakistan", "website": "https://charcoal.com.pk", "industry": "Men's Apparel & Formal Wear"},
    {"company": "Edenrobe", "decision_maker": "Junaid Dandia", "role": "Director", "niche": "d2c", "region": "Pakistan", "website": "https://edenrobe.com", "industry": "Apparel & Kids Wear"},
    {"company": "Generation", "decision_maker": "Nosheen Khan", "role": "Founder", "niche": "d2c", "region": "Pakistan", "website": "https://generation.com.pk", "industry": "Contemporary Women's Pret"},
    {"company": "Asim Jofa", "decision_maker": "Asim Jofa", "role": "Founder & Designer", "niche": "d2c", "region": "Pakistan", "website": "https://asimjofa.com", "industry": "Designer Luxury Lawn"},
    {"company": "Bonanza Satrangi", "decision_maker": "Hanif Bilwani", "role": "CEO", "niche": "d2c", "region": "Pakistan", "website": "https://bonanzasatrangi.com", "industry": "Ready-to-Wear & Beauty"},
    {"company": "Bagallery", "decision_maker": "Mina Salman", "role": "Co-Founder", "niche": "d2c", "region": "Pakistan", "website": "https://bagallery.com", "industry": "Beauty & Fashion E-Commerce"},
    {"company": "Stylo Shoes", "decision_maker": "Javed Siddique", "role": "Chairman", "niche": "d2c", "region": "Pakistan", "website": "https://stylo.pk", "industry": "Footwear & Accessories Retail"},
    {"company": "Borjan", "decision_maker": "Naveed Ijaz", "role": "CEO", "niche": "d2c", "region": "Pakistan", "website": "https://borjan.com.pk", "industry": "Footwear & Handbags"},
    {"company": "Limelight", "decision_maker": "Waseem Riaz", "role": "CEO", "niche": "d2c", "region": "Pakistan", "website": "https://limelight.pk", "industry": "Fast Fashion & Accessories"},

    # --- Real Estate & Construction ---
    {"company": "Imarat Group", "decision_maker": "Shafiq Akbar", "role": "Chairman", "niche": "real-estate", "region": "Pakistan", "website": "https://imarat.com.pk", "industry": "Real Estate Developments & Hospitality"},
    {"company": "Graana", "decision_maker": "Farhan Javed", "role": "Group Director", "niche": "real-estate", "region": "Pakistan", "website": "https://graana.com", "industry": "Real Estate & Property Platform"},
    {"company": "Zameen Group", "decision_maker": "Zeeshan Ali Khan", "role": "CEO", "niche": "real-estate", "region": "Pakistan", "website": "https://zameen.com", "industry": "Property Development & Marketing"},
    {"company": "Habib Construction Services", "decision_maker": "Shahid Saleem", "role": "Managing Director", "niche": "real-estate", "region": "Pakistan", "website": "https://hcs.com.pk", "industry": "Mega Infrastructure & Civil Projects"},
    {"company": "Izhar Group", "decision_maker": "Ayub Sabir Izhar", "role": "Chairman", "niche": "real-estate", "region": "Pakistan", "website": "https://izhar.com", "industry": "Construction & Precast Engineering"},

    # --- Healthcare & Diagnostic Clinics ---
    {"company": "Chughtai Lab", "decision_maker": "Dr. Omar Chughtai", "role": "Director Operations", "niche": "healthcare", "region": "Pakistan", "website": "https://chughtailab.com", "industry": "Pathology & Diagnostic Clinics"},
    {"company": "Shaukat Khanum", "decision_maker": "Dr. Faisal Sultan", "role": "CEO", "niche": "healthcare", "region": "Pakistan", "website": "https://shaukatkhanum.org.pk", "industry": "Specialized Hospital & Research"},
    {"company": "Marham", "decision_maker": "Ehsan Imam", "role": "Founder & CEO", "niche": "healthcare", "region": "Pakistan", "website": "https://marham.pk", "industry": "Digital Healthcare & Clinic Network"},
    {"company": "Cosmetique Dermatology", "decision_maker": "Prof. Dr. Azim Jahangir Khan", "role": "CEO & Chief Dermatologist", "niche": "healthcare", "region": "Pakistan", "website": "https://cosmetique.com.pk", "industry": "Cosmetic Dermatology & Hair Transplant"},
    {"company": "Rahman & Rahman Dental", "decision_maker": "Dr. Amin Rahman", "role": "Managing Director", "niche": "healthcare", "region": "Pakistan", "website": "https://randr.com.pk", "industry": "Specialized Dental Clinics"},

    # --- B2B, Manufacturing & Export ---
    {"company": "Interloop Limited", "decision_maker": "Navid Fazil", "role": "CEO", "niche": "b2b", "region": "Pakistan", "website": "https://interloop-pk.com", "industry": "Textile & Hosiery Global Exporter"},
    {"company": "Kohinoor Textile Mills", "decision_maker": "Taufiq Sayeed Saigol", "role": "CEO", "niche": "b2b", "region": "Pakistan", "website": "https://ktml.com", "industry": "Textile Manufacturing & Exports"},
    {"company": "Soorty Enterprises", "decision_maker": "Shahid Soorty", "role": "Managing Director", "niche": "b2b", "region": "Pakistan", "website": "https://soorty.com", "industry": "Global Denim & Apparel Manufacturer"},
    {"company": "Artistic Milliners", "decision_maker": "Omer Ahmed", "role": "CEO", "niche": "b2b", "region": "Pakistan", "website": "https://artisticmilliners.com", "industry": "Denim Manufacturing & Green Energy"},
    {"company": "English Biscuit Manufacturers", "decision_maker": "Dr. Zeelaf Munir", "role": "Managing Director & CEO", "niche": "b2b", "region": "Pakistan", "website": "https://ebm.com.pk", "industry": "FMCG & Biscuit Manufacturing"},
    {"company": "Shan Foods", "decision_maker": "Sikandar Sultan", "role": "Founder & Co-Chairman", "niche": "b2b", "region": "Pakistan", "website": "https://shanfoods.com", "industry": "Spices & Food Packaging Exporter"},

    # =========================================================================
    # INTERNATIONAL (UAE Luxury Real Estate, US/UK D2C, Private Clinics)
    # =========================================================================
    # --- UAE Luxury Real Estate & Developers ---
    {"company": "DAMAC Properties", "decision_maker": "Hussain Sajwani", "role": "Founder & Chairman", "niche": "real-estate", "region": "International", "website": "https://damacproperties.com", "industry": "Ultra-Luxury Residential & Towers"},
    {"company": "Emaar Properties", "decision_maker": "Mohamed Alabbar", "role": "Founder & Managing Director", "niche": "real-estate", "region": "International", "website": "https://emaar.com", "industry": "Master Communities & Luxury Living"},
    {"company": "Sobha Realty Dubai", "decision_maker": "PNC Menon", "role": "Founder & Chairman", "niche": "real-estate", "region": "International", "website": "https://sobharealty.com", "industry": "Luxury Waterfront Developments"},
    {"company": "Omniyat", "decision_maker": "Mahdi Amjad", "role": "Founder & Executive Chairman", "niche": "real-estate", "region": "International", "website": "https://omniyat.com", "industry": "Architectural Landmarks & Hospitality"},
    {"company": "Danube Properties", "decision_maker": "Rizwan Sajan", "role": "Founder & Chairman", "niche": "real-estate", "region": "International", "website": "https://danubeproperties.com", "industry": "Affordable Luxury Housing Dubai"},
    {"company": "Binghatti Developers", "decision_maker": "Muhammad Binghatti", "role": "CEO", "niche": "real-estate", "region": "International", "website": "https://binghatti.com", "industry": "Branded Luxury Towers"},
    {"company": "Select Group", "decision_maker": "Rahail Aslam", "role": "Founder & Group CEO", "niche": "real-estate", "region": "International", "website": "https://select-group.ae", "industry": "Waterfront Real Estate Developments"},

    # --- US & UK High-Ticket D2C Brands ---
    {"company": "Allbirds", "decision_maker": "Tim Brown", "role": "Co-Founder", "niche": "d2c", "region": "International", "website": "https://allbirds.com", "industry": "Sustainable Footwear & Apparel"},
    {"company": "Gymshark", "decision_maker": "Ben Francis", "role": "Founder & CEO", "niche": "d2c", "region": "International", "website": "https://gymshark.com", "industry": "Performance Fitness Apparel"},
    {"company": "Glossier", "decision_maker": "Emily Weiss", "role": "Founder", "niche": "d2c", "region": "International", "website": "https://glossier.com", "industry": "Direct-to-Consumer Beauty"},
    {"company": "Warby Parker", "decision_maker": "Neil Blumenthal", "role": "Co-Founder & Co-CEO", "niche": "d2c", "region": "International", "website": "https://warbyparker.com", "industry": "Prescription Eyewear & Retail"},
    {"company": "Hims & Hers", "decision_maker": "Andrew Dudum", "role": "Co-Founder & CEO", "niche": "d2c", "region": "International", "website": "https://forhims.com", "industry": "Digital Health & Telemedicine Wellness"},
    {"company": "Away Travel", "decision_maker": "Jen Rubio", "role": "Co-Founder & CEO", "niche": "d2c", "region": "International", "website": "https://awaytravel.com", "industry": "Premium Luggage & Travel Accessories"},
    {"company": "Casper", "decision_maker": "Philip Krim", "role": "Co-Founder", "niche": "d2c", "region": "International", "website": "https://casper.com", "industry": "Sleep Products & Mattresses"},
    {"company": "Brooklinen", "decision_maker": "Rich Fulop", "role": "Co-Founder & CEO", "niche": "d2c", "region": "International", "website": "https://brooklinen.com", "industry": "Luxury Home & Bedding"},
    {"company": "Liquid Death", "decision_maker": "Mike Cessario", "role": "Founder & CEO", "niche": "d2c", "region": "International", "website": "https://liquiddeath.com", "industry": "Healthy Canned Beverage"},
    {"company": "Vuori", "decision_maker": "Joe Kudla", "role": "Founder & CEO", "niche": "d2c", "region": "International", "website": "https://vuoriclothing.com", "industry": "Premium Coastal Performance Apparel"},
    {"company": "Ridge Wallet", "decision_maker": "Daniel Kane", "role": "Co-Founder & CEO", "niche": "d2c", "region": "International", "website": "https://ridge.com", "industry": "Minimalist Everyday Accessories"},
    {"company": "Curology", "decision_maker": "Dr. David Lortscher", "role": "Founder & CEO", "niche": "d2c", "region": "International", "website": "https://curology.com", "industry": "Prescription Skincare"},
    {"company": "FIGS", "decision_maker": "Trina Spear", "role": "Co-Founder & CEO", "niche": "d2c", "region": "International", "website": "https://wearfigs.com", "industry": "Direct-to-Consumer Medical Apparel"},
    {"company": "Caraway Home", "decision_maker": "Jordan Nathan", "role": "Founder & CEO", "niche": "d2c", "region": "International", "website": "https://carawayhome.com", "industry": "Non-Toxic Ceramic Cookware"},

    # --- High-Ticket Clinics & Healthcare ---
    {"company": "Harley Street Dental Clinic", "decision_maker": "Dr. Neesha Patel", "role": "Clinical Director", "niche": "healthcare", "region": "International", "website": "https://harleystreetdentalclinic.co.uk", "industry": "Private Dental Surgery London"},
    {"company": "London Aesthetic Clinic", "decision_maker": "Medical Director", "role": "Managing Director", "niche": "healthcare", "region": "International", "website": "https://londonaestheticclinic.co.uk", "industry": "Cosmetic Surgery & Aesthetics"},
    {"company": "Beverly Hills Dental Center", "decision_maker": "Dr. Kourosh Maddahi", "role": "Founder", "niche": "healthcare", "region": "International", "website": "https://beverlyhillsdentalcenter.com", "industry": "Cosmetic Dentistry Beverly Hills"},
    {"company": "Emirates Hospital Clinics", "decision_maker": "Dr. Maan Jamal", "role": "Medical Director", "niche": "healthcare", "region": "International", "website": "https://emirateshospital.ae", "industry": "Specialty Clinics & Surgery Dubai"},
    {"company": "Mediclinic Middle East", "decision_maker": "Hein van Eck", "role": "Chief Executive Officer", "niche": "healthcare", "region": "International", "website": "https://mediclinic.ae", "industry": "Private Healthcare Hospital Network"},

    # --- Luxury Hospitality & Resorts ---
    {"company": "Jumeirah Group", "decision_maker": "Katerina Giannouka", "role": "CEO", "niche": "hospitality", "region": "International", "website": "https://jumeirah.com", "industry": "Luxury Hotels & Hospitality (Burj Al Arab)"},
    {"company": "Soho House", "decision_maker": "Nick Jones", "role": "Founder", "niche": "hospitality", "region": "International", "website": "https://sohohouse.com", "industry": "Private Members Club & Boutique Hotels"},
]


def run_lead_generation(
    target_count: int = 100,
    region_filter: str = "all",
    niche_filter: str = "all",
    profile_path: str = None,
    output_path: str = "pragtify_leads_latest.csv",
    concurrency: int = 10
):
    start_time = time.time()
    console.print()
    console.print("[bold white on #10b981]  SCOUT // NON-TECH CLIENT DISCOVERY ENGINE  [/bold white on #10b981]")
    console.print(f"[dim]Goal: High-value non-tech clients with real budgets (D2C, Real Estate, Clinics, B2B)[/dim]")
    console.print(f"[cyan]Target: [bold]{target_count}[/bold] leads | Region: [bold]{region_filter.upper()}[/bold] | Niche: [bold]{niche_filter.upper()}[/bold] | Workers: [bold]{concurrency}[/bold][/cyan]\n")

    # 1. Initialize Memory, Enricher & Sniffer
    memory = AgencyMemory(profile_path=profile_path)
    matcher = LeadMatcher(memory=memory)
    enricher = LeadEnricher()
    sniffer = TechSniffer()

    # 2. Filter Candidate Directory
    candidates = []
    reg_clean = region_filter.lower().strip()
    niche_clean = niche_filter.lower().strip()

    for item in NON_TECH_CLIENTS:
        # Check region
        if reg_clean != "all":
            if item["region"].lower() != reg_clean:
                continue
        # Check niche
        if niche_clean != "all":
            if item["niche"].lower() != niche_clean:
                continue
        candidates.append(item)

    if not candidates:
        console.print(f"[bold red]No targets matched filters region='{region_filter}', niche='{niche_filter}'[/bold red]")
        return None, None

    console.print(f"[bold yellow][1/3] Selected {len(candidates)} high-potential non-tech business targets...[/bold yellow]")

    # 3. Concurrently inspect tech stack & enrich contact info
    console.print(f"[bold yellow][2/3] Crawling Domains, Sniffing Tech Stacks & Extracting Direct Contacts...[/bold yellow]")
    processed_leads = []

    def _worker(c):
        try:
            profile = {
                "username": c["company"].lower().replace(" ", "_"),
                "full_name": f"{c['decision_maker']} ({c['role']})",
                "headline": f"{c['role']} at {c['company']}",
                "company": c["company"],
                "website": c["website"],
                "industry": c["industry"],
                "bio": f"{c['company']} is a leading business in {c['industry']}. Seeking web performance, higher sales conversions, and customer workflow automation.",
                "location": c["region"],
            }
            enriched = enricher.enrich_lead(profile)
            matched = matcher.match_lead(enriched)
            matched["target_niche"] = c["niche"]
            return matched
        except Exception as e:
            return None

    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as executor:
        futures = {executor.submit(_worker, it): it for it in candidates}
        for future in as_completed(futures):
            res = future.result()
            if res:
                processed_leads.append(res)
                name = res.get("company")
                dm = (res.get("full_name") or "").split("(")[0].strip()
                reg = res.get("market_region")
                has_email = bool(res.get("email"))
                has_phone = bool(res.get("phone"))
                has_wa = bool(res.get("whatsapp_chat_link"))

                status_parts = []
                if has_email:
                    status_parts.append(f"[green]✉ {res['email'][:24]}[/green]")
                if has_phone:
                    status_parts.append(f"[bold cyan]☎ {res['phone']}[/bold cyan]")
                if has_wa:
                    status_parts.append("[bold green]WA[/bold green]")

                opps = res.get("tech_opportunities", [])
                opp_str = f" | [yellow]{opps[0][:35]}...[/yellow]" if opps else ""
                status_str = " | ".join(status_parts) if status_parts else "[dim]Domain verified[/dim]"
                console.print(f"  [green]✓[/green] [{len(processed_leads):03d}/{min(target_count, len(candidates))}] [{reg}] [bold white]{name[:18]}[/bold white] ({dm[:14]}) -> {status_str}{opp_str}")

                if len(processed_leads) >= target_count:
                    for f in futures:
                        f.cancel()
                    break

    console.print(f"\n[bold green]Enrichment Complete in {time.time() - start_time:.1f}s! Total Validated Non-Tech Leads: {len(processed_leads)}[/bold green]")

    # 4. Save to CSV
    console.print(f"[bold yellow][3/3] Exporting CSV and Syncing Minimal AI Dashboard...[/bold yellow]")
    csv_latest = Path(output_path)
    csv_timestamp = Path(f"leads_export_{int(time.time())}.csv")

    fieldnames = [
        "company",
        "full_name",
        "market_region",
        "target_niche",
        "agency_fit_score",
        "email",
        "phone",
        "whatsapp_chat_link",
        "website",
        "matched_services",
        "matched_portfolio",
        "tech_opportunities",
        "recommended_pitch",
        "headline",
        "bio",
        "industry",
        "linkedin_url",
        "instagram_url",
    ]

    saved_csv_files = []
    for p in [csv_latest, csv_timestamp]:
        try:
            with open(p, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                for lead in processed_leads:
                    lead_copy = dict(lead)
                    if isinstance(lead_copy.get("tech_opportunities"), list):
                        lead_copy["tech_opportunities"] = " | ".join(lead_copy["tech_opportunities"])
                    if isinstance(lead_copy.get("detected_technologies"), list):
                        lead_copy["detected_technologies"] = ", ".join(lead_copy["detected_technologies"])
                    writer.writerow(lead_copy)
            saved_csv_files.append(p)
            console.print(f"  [green]✓[/green] Successfully saved to [bold white]{p}[/bold white]")
        except PermissionError:
            console.print(f"  [yellow]⚠ Warning: Could not write to {p} (file open in another app).[/yellow]")

    # 5. Automatically trigger dashboard refresh
    dash_script = Path("generate_minimal_dashboard.py")
    if dash_script.exists():
        try:
            subprocess.run([sys.executable, str(dash_script)], check=True)
            console.print(f"  [green]✓[/green] Recompiled minimalist AI dashboard: [bold white]leads_dashboard.html[/bold white]")
        except Exception as e:
            console.print(f"  [dim]Could not recompile dashboard: {e}[/dim]")

    # 6. Summary Table
    table = Table(
        title=f"SCOUT NON-TECH CLIENTS INTELLIGENCE ({len(processed_leads)} Leads)",
        box=box.ROUNDED,
        header_style="bold magenta"
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Company", style="bold white", width=18)
    table.add_column("Decision Maker", style="cyan", width=20)
    table.add_column("Region", style="yellow", width=12)
    table.add_column("Niche", style="magenta", width=12)
    table.add_column("Fit Score", justify="center", width=10)
    table.add_column("Direct Contact", style="green", width=22)
    table.add_column("Key Opportunity / Hook", style="white", width=35)

    for idx, l in enumerate(processed_leads[:20], 1):
        score = l.get("agency_fit_score", 0)
        score_style = "bold green" if score >= 90 else "bold yellow"
        dm = (l.get("full_name") or "").split("(")[0].strip()
        contact = l.get("phone") or l.get("email") or "Web Form"
        opps = l.get("tech_opportunities")
        if isinstance(opps, list):
            opps_str = opps[0] if opps else "Modernization"
        else:
            opps_str = str(opps).split("|")[0].strip() if opps else "Modernization"

        table.add_row(
            str(idx),
            l.get("company", "")[:18],
            dm[:20],
            l.get("market_region", "N/A"),
            l.get("target_niche", "N/A"),
            f"[{score_style}]{score}/100[/{score_style}]",
            contact[:22],
            opps_str[:35]
        )

    console.print("\n")
    console.print(table)
    console.print()
    return saved_csv_files[0] if saved_csv_files else csv_latest


def main():
    parser = argparse.ArgumentParser(description="Scout High-Scale Non-Tech Client Discovery & Intelligence Engine")
    parser.add_argument("--target", type=int, default=100, help="Target number of non-tech clients to discover (default: 100)")
    parser.add_argument("--region", type=str, default="all", choices=["all", "india", "pakistan", "international"], help="Filter by region (all, india, pakistan, international)")
    parser.add_argument("--niche", type=str, default="all", choices=["all", "d2c", "real-estate", "healthcare", "b2b", "hospitality"], help="Filter by niche (all, d2c, real-estate, healthcare, b2b, hospitality)")
    parser.add_argument("--profile", type=str, default=None, help="Path to custom agency profile JSON")
    parser.add_argument("--output", type=str, default="pragtify_leads_latest.csv", help="Custom output CSV path")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent worker threads (default: 10)")

    args = parser.parse_args()
    run_lead_generation(
        target_count=args.target,
        region_filter=args.region,
        niche_filter=args.niche,
        profile_path=args.profile,
        output_path=args.output,
        concurrency=args.concurrency
    )


if __name__ == "__main__":
    main()
