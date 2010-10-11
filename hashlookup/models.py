from django.db import models

class Manufacturer(models.Model):
    """NSRL Manufacturer model this maps to the NSRLMfg.txt file"""
    mfg_id = models.AutoField(primary_key=True)
    mfg_code = models.CharField(max_length=32, unique=True)
    mfg_name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.mfg_name

class OperatingSystem(models.Model):
    """NSRL Operating System model this maps to the NSRLOS.txt file"""
    os_id = models.AutoField(primary_key=True)
    os_code = models.CharField(max_length=32, unique=True)
    os_name = models.CharField(max_length=128)
    os_version = models.CharField(max_length=32)
    mfg_id = models.ForeignKey(Manufacturer, to_field='mfg_id',
                               related_name='+')
    mfg_code = models.ForeignKey(Manufacturer, to_field='mfg_code',
                                 related_name='+')

    def __unicode__(self):
        return u" ".join([self.os_name, self.os_version])

class Product(models.Model):
    """NSRL Product model this maps to the NSRLProd.txt file"""
    prod_id = models.AutoField(primary_key=True)
    prod_code = models.PositiveIntegerField()
    prod_name = models.CharField(max_length=128)
    prod_version = models.CharField(max_length=32)
    prod_lang = models.CharField(max_length=32)
    prod_app_type = models.CharField(max_length=64)
    os_id = models.ForeignKey(OperatingSystem, to_field='os_id',
                              related_name='+')
    mfg_id = models.ForeignKey(Manufacturer, to_field='mfg_id',
                               related_name='+')
    os_code = models.ForeignKey(OperatingSystem, to_field='os_code',
                                related_name='+')
    mfg_code = models.ForeignKey(Manufacturer, to_field='mfg_code',
                                 related_name='+')

    class Meta:
        unique_together = (("prod_code", "os_id", "mfg_id", "prod_lang"),)

    def __unicode__(self):
        return u" ".join([self.prod_name, self.prod_version, self.prod_lang])

class File(models.Model):
    """NSRL File model this maps to the NSRLFile.txt file"""
    file_sha1 = models.CharField(max_length=40)
    file_md5 = models.CharField(max_length=32)
    file_crc32 = models.CharField(max_length=8)
    file_name = models.CharField(max_length=256)
    file_size = models.PositiveIntegerField()
    file_spec_code = models.CharField(max_length=32)
    prod_id = models.ForeignKey(Product, to_field='prod_id', related_name='+')
    os_id = models.ForeignKey(OperatingSystem, to_field='os_id',
                              related_name='+')
    os_code =  models.ForeignKey(OperatingSystem, to_field='os_code',
                                 related_name='+')

    class Meta:
        unique_together = (("file_sha1", "file_name", "prod_id", "os_id"),)

    def __unicode__(self):
        return " ".join([self.file_name,
                         unicode(self.file_size),
                         self.file_sha1])

