from django.db import models

# Create your models here.
class Logo(models.Model):
  image=models.ImageField(null=True)
  text=models.CharField(max_length=100,null=True)



class Banner(models.Model):
  image=models.ImageField(null=True,upload_to='banner_images/')
  title=models.CharField(max_length=40,null=False)
  description=models.CharField(null=False, max_length=50)



class About(models.Model):
  image=models.ImageField(null=True,upload_to='about_image/')
  title=  title=models.CharField(max_length=40,blank=True,null=False,default='About us')
  description=models.TextField(null=False)



class FooterColumn(models.Model):
  title=models.CharField(max_length=150)

  def __str__(self):
    return self.title


class FooterListItem(models.Model):
  name=models.CharField(max_length=150)
  link=models.CharField(max_length=250,blank=True,null=True)
  footer_column=models.ForeignKey(FooterColumn,on_delete=models.CASCADE,related_name='footer_list_item')

  def __str__(self):
    return self.name




