#!/usr/bin/env python
from django.core.management import setup_environ
import settings
setup_environ(settings)
import sys
import os
import csv
import settings
import os.path
from django.db import transaction
from django.db.utils import IntegrityError
from hashlookup.models import Manufacturer, OperatingSystem, Product, File

def test_encoding(s, enc):
    """Test the given encoding"""
    try:
        s.decode(enc)
    except UnicodeDecodeError, e:
        return False
    except LookupError, e:
        return False
    return True

def get_encoding(s):
    """Check that this string is utf-8, if it isn't ask user"""
    if test_encoding(s, 'utf-8'):
        return 'utf-8'
    if test_encoding(s, 'latin_1'):
    	return 'latin_1'
    while(True):
        enc = raw_input('Unknown Encoding: "%s"\n-->' % s)
        if test_encoding(s, enc):
            return enc

def normalize_encoding(s):
    return s.decode(get_encoding(s))

@transaction.commit_on_success
def mfg_import(base_path, mfg_data=u'NSRLMfg.txt'):
    """Read the CSV file and import the manufacturer data"""
    nsrl_mfg = csv.DictReader(open(os.path.join(base_path, mfg_data), 'rb'))
    for mfg in nsrl_mfg:
        try:
            m = Manufacturer(mfg_code=mfg['MfgCode'], mfg_name=mfg['MfgName'])
            m.save()
        except IntegrityError, e:
            print "Duplicate Manufacturer:", m

@transaction.commit_on_success
def os_import(base_path, os_data=u'NSRLOS.txt'):
    """Read the CSV file and import the operating system data"""
    nsrl_os = csv.DictReader(open(os.path.join(base_path, os_data), 'rb'))
    for osys in nsrl_os:
        try:
            mfg = Manufacturer.objects.get(mfg_code=osys['MfgCode'])
            o = OperatingSystem(os_code=osys['OpSystemCode'],
                                os_name=osys['OpSystemName'],
                                os_version=osys['OpSystemVersion'],
                                mfg_id=mfg,
                                mfg_code=mfg)
            o.save()
        except IntegrityError, e:
            print "Duplicate OS:", o

@transaction.commit_on_success
def prod_import(base_path, prod_data=u'NSRLProd.txt'):
    """Read the CSV file and import the operating system data"""
    nsrl_prod = csv.DictReader(open(os.path.join(base_path, prod_data), 'rb'))
    for prod in nsrl_prod:
        try:
            mfg = Manufacturer.objects.get(mfg_code=prod['MfgCode'])
            osys = OperatingSystem.objects.get(os_code=prod['OpSystemCode'])
            p = Product(prod_code = prod['ProductCode'],
                        prod_name = prod['ProductName'],
                        prod_version = prod['ProductVersion'],
                        prod_lang = prod['Language'],
                        prod_app_type = prod['ApplicationType'],
                        os_id = osys, os_code = osys,
                        mfg_id = mfg, mfg_code = mfg)
            p.save()
        except IntegrityError, e:
            print "Duplicate Product:", p

@transaction.commit_on_success
def file_import(base_path, file_data=u'NSRLFile.txt'):
    """Read the CSV file and import the file data"""
    nsrl_file = csv.DictReader(open(os.path.join(base_path, file_data), 'rb'))
    for file in nsrl_file:
        try:
            prod = Product.objects.filter(prod_code=file['ProductCode'],
                                          os_code=file['OpSystemCode'])
            if len(prod) == 0:
                # This happens when OpSystemCode is "TBD"
                prod = Product.objects.filter(prod_code=file['ProductCode'])
                osys = None
            else:
                osys = OperatingSystem.objects.get(os_code=file['OpSystemCode'])
            for p in prod:
                try:
                    if osys is None:
                        osc = p.os_id
                    else:
                        osc = osys
                    f = File(file_sha1=file['SHA-1'],
                             file_md5=file['MD5'],
                             file_crc32=file['CRC32'],
                             file_name=normalize_encoding(file['FileName']),
                             file_size=file['FileSize'],
                             file_spec_code=file['SpecialCode'],
                             prod_id=p,
                             os_id=osc,
                             os_code=osc)
                    f.save()
                except IntegrityError, e:
                    print "Duplicate File:", f
        except IntegrityError, e:
            print type(e)

if __name__ == "__main__":
    base_dir = sys.argv[1]
    mfg_import(base_dir)
    os_import(base_dir)
    prod_import(base_dir)
    file_import(base_dir)
