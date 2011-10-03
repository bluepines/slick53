# slick53
A python interface for AWS Route53.

 * Original Author: Brad Carleton
 * Company: Blue Pines Technologies
 * Website: [http://www.bluepines.org](http://www.bluepines.org)
 * Blog: [An introduction to Slick53](http://www.bluepines.org/blog/slick53-python-interface-aws-route53)

## Overview
This module provides a slick, super-easy interface for dealing with
AWS Route53.  It is built on top of the boto library.

## Installation
How to Install from github\:

1. git clone git://github.com/bluepines/slick53.git
2. cd slick53
3. sudo python setup.py install

You also need to set the following environment variables:
    AWS_ACCESS_KEY_ID
    AWS_SECRET_KEY_ID

## Usage
I wrote this library to make dealing with Amazon AWS a lot easier.
Now you can write code like the following:

```python
>>> from slick53 import route53
>>> zone = route53.create_zone('example.com')
>>> zone.add_a('example.com', '182.12.142.12')
>>> zone.add_cname('www.example.com', 'example.com')
>>> zone.add_mx(['10 mail.example.com', '20 mail.example.com']
```

Now what just happended.  On line two we create the zone.  Then we create 
an A record for the naked domain, followed by a cname for the ‘www’ subdomain 
which points back to the naked domain.  Then we also added two MX records 
for our mail exchangers.  Also, you don’t need to worry about trailing dots 
and fully qualified domain names, because that is handled automatically.

Now, once we have all of our records up and running let’s see what we can do.

```python
>>>  route53.get_zones()
[<Zone:example.com>, <Zone:bluepines.org>]
>>> zone = route53.get_zone('example.com')
>>> for record in zone.get_records():
    print record
<Record:A:example.com.>
<Record:CNAME:www.example.com.>
<Record:MX:example.com.>
<Record:NS:example.com.>
<Record:SOA:example.com.>
>>> zone.get_nameservers()
[u'ns-1249.awsdns-28.org.', u'ns-902.awsdns-48.net.', u'ns-257.awsdns-32.com.', u'ns-1555.awsdns-02.co.uk.']
```

So here we grabbed the zone by putting in it’s name, and then we printed 
all the records that we have added so far. (Notice, every zone you create 
has an NS record and SOA record automatically created by Route53 when you 
create the zone.) We also printed out the list of name servers that Amazon 
started us out with.  You add the nameservers to your domain 
registrar to actually switch to Amazon’s DNS service.  I would recommend 
migrating a non-critical domain to start to make sure that you understand 
the process before moving your big domain with hundreds of records over to Route53. 

Now we can remove all these records and the zone itself like so:

```python
>>> zone = route53.get_zone('example.com')
>>> zone.delete_a('example.com')
>>> zone.delete_cname('www.example.com')
>>> zone.delete_mx()
>>> zone.delete()
```

If anyone has any questions, bugs or issues then feel free to ask.  
Hopefully, this will make your life with Route53 significantly easier.

## Dependencies
boto - must have at least version 2.0

