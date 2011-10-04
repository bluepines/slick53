
import boto
from boto.route53.connection import Route53Connection
from boto.route53.record import ResourceRecordSets
from boto.route53.record import Record

__all__ = []

route53 = boto.connect_route53()
default_ttl = 60

def create_zone(self, name):
    """ Create new hosted zone."""
    zone = route53.create_hosted_zone(name)
    zone = zone['CreateHostedZoneResponse']['HostedZone']
    return Zone(zone)

def get_zones(self):
    """ Retrieve a list of all hosted zones."""
    zones = route53.get_all_hosted_zones()
    zones = zones['ListHostedZonesResponse']['HostedZones']
    zone_list = []
    for zone in zones:
        zone_list.append(Zone(zone)) 
    return zone_list

def get_zone(self, name):
    """ Retrieve the hosted zone supplied by name."""
    zones = self.get_zones()
    for zone in zones:
        if name + '.' == zone.name:
            return zone

def make_qualified(self, value):
    """ Turn unqualified domain names into qualified ones."""
    if type(value) in [list, tuple, set]:
        new_list = []
        for record in value:
            if record[-1] != '.':
                new_list.append(record + '.')
            else:
                new_list.append(record)
        return new_list
    else:
        value = value.strip()
        if value[-1] != '.':
            value = value + '.'
        return value

def set_default_ttl(self, ttl):
    default_ttl = ttl

Route53Connection.get_zones = get_zones
Route53Connection.get_zone = get_zone
Route53Connection.create_zone = create_zone
Route53Connection.make_qualified = make_qualified

def repr_record(self):
    return '<Record:%s:%s:%s>' % (self.type, self.name, self.resource_records)

Record.__repr__ = repr_record

def repr_record_set(self):
    record_list = ','.join([record.__repr__() for record in self])
    return '[%s]' % record_list
    
ResourceRecordSets.__repr__ = repr_record_set

class Zone(object):
    def __init__(self, zone_dict):
        for key in zone_dict:
            if key == 'Id':
                self.id = zone_dict['Id'].replace('/hostedzone/','')
            else:    
                self.__setattr__(key.lower(), zone_dict[key])
    def __repr__(self):
        return '<Zone:%s>' % self.name

    def add_record(self, resource_type, name, value, ttl=60, comment=""):
        """Add a new record to a zone"""
        changes = ResourceRecordSets(route53, self.id, comment)
        change = changes.add_change("CREATE", name, resource_type, ttl)
        if type(value) in [list, tuple, set]:
            for record in value:
                change.add_value(record)
        else:
            change.add_value(value)
        status = Status(changes.commit()['ChangeResourceRecordSetsResponse']['ChangeInfo'])

    def update_record(self, resource_type, name, old_value, new_value, old_ttl, new_ttl=None, comment=""):
        new_ttl = new_ttl or default_ttl
        changes = ResourceRecordSets(route53, self.id, comment)
        change = changes.add_change("DELETE", name, resource_type, old_ttl)
        if type(old_value) in [list, tuple, set]:
            for record in old_value:
                change.add_value(record)
        else:
            change.add_value(old_value)
        change = changes.add_change('CREATE', name, resource_type, new_ttl)
        if type(new_value) in [list, tuple, set]:
            for record in new_value:
                change.add_value(record)
        else:
            change.add_value(new_value)
        status = Status(changes.commit()['ChangeResourceRecordSetsResponse']['ChangeInfo'])

    def delete_record(self, resource_type, name, value, ttl=None, comment=""):
        """Delete a record from a zone"""
        ttl = ttl or default_ttl
        changes = ResourceRecordSets(route53, self.id, comment)
        change = changes.add_change("DELETE", name, resource_type, ttl)
        if type(value) in [list, tuple, set]:
            for record in value:
                change.add_value(record)
        else:
            change.add_value(value)
        status = Status(changes.commit()['ChangeResourceRecordSetsResponse']['ChangeInfo'])

    def add_cname(self, name, value, ttl=None, comment=""):
        ttl = ttl or default_ttl
        name = route53.make_qualified(name)
        value = route53.make_qualified(value)
        return self.add_record(resource_type='CNAME', 
                               name=name, 
                               value=value, 
                               ttl=ttl, 
                               comment=comment)

    def add_a(self, name, value, ttl=None, comment=""):
        """Add an A record to the zone."""
        ttl = ttl or default_ttl
        name = route53.make_qualified(name)
        return self.add_record(resource_type='A', 
                               name=name, 
                               value=value, 
                               ttl=ttl, 
                               comment=comment)

    def add_mx(self, records, ttl=None, comment=""):
        """Add an MX record to the zone."""
        ttl = ttl or default_ttl
        records = route53.make_qualified(records)
        return self.add_record(resource_type='MX', 
                               name=self.name, 
                               value=records, 
                               ttl=ttl, 
                               comment=comment)


    def get_cname(self, name):
        """ Get the given CNAME record."""
        name = route53.make_qualified(name)
        for record in self.get_records():
            if record.name == name and record.type == 'CNAME':
                return record

    def get_a(self, name):
        """ Get the given A record."""
        name = route53.make_qualified(name)
        for record in self.get_records():
            if record.name == name and record.type == 'A':
                return record

    def get_mx(self):
        """ Get all MX records."""
        for record in self.get_records():
            if record.type == 'MX':
                return record
    
    def update_cname(self, name, value, ttl=None, comment=""):
        """ Update the given CNAME record to a new value and ttl."""
        name = route53.make_qualified(name)
        value = route53.make_qualified(value)
        old_record = self.get_cname(name)
        ttl = ttl or old_record.ttl
        return self.update_record(resource_type='CNAME', 
                                  name=name, 
                                  old_value=old_record.resource_records, 
                                  new_value=value, 
                                  old_ttl=old_record.ttl, 
                                  new_ttl=ttl, 
                                  comment=comment)
        
    def update_a(self, name, value, ttl=None, comment=""):
        """ Update the given A record to a new value and ttl."""
        name = route53.make_qualified(name)
        old_record = self.get_a(name)
        ttl = ttl or old_record.ttl
        return self.update_record(resource_type='A', 
                                  name=name, 
                                  old_value=old_record.resource_records, 
                                  new_value=value, 
                                  old_ttl=old_record.ttl, 
                                  new_ttl=ttl, 
                                  comment=comment)

    def update_mx(self, value, ttl=None, comment=""):
        """ Update the MX records to the new value and ttl."""
        value = route53.make_qualified(value)
        old_record = self.get_mx()
        ttl = ttl or old_record.ttl
        return self.update_record(resource_type='MX', 
                                  name=self.name, 
                                  old_value=old_record.resource_records, 
                                  new_value=value, 
                                  old_ttl=old_record.ttl, 
                                  new_ttl=ttl, 
                                  comment=comment)


    def delete_cname(self,name):
        """ Delete the given CNAME record for this zone."""
        record = self.get_cname(route53.make_qualified(name))
        return self.delete_record(resource_type=record.type, 
                                  name=record.name, 
                                  value=record.resource_records, 
                                  ttl=record.ttl)

    def delete_a(self,name):
        """ Delete the given A record for this zone."""
        record = self.get_a(route53.make_qualified(name))
        return self.delete_record(resource_type=record.type, 
                                  name=record.name, 
                                  value=record.resource_records, 
                                  ttl=record.ttl)

    def delete_mx(self):
        """ Delete all MX records for the zone."""
        record = self.get_mx()
        return self.delete_record(resource_type=record.type, 
                                  name=record.name, 
                                  value=record.resource_records, 
                                  ttl=record.ttl)

    def get_records(self, type=None):
        """ Get a list of all records for this zone."""
        return route53.get_all_rrsets(self.id, type=type)

    def delete(self):
        """ Delete this zone."""
        route53.delete_hosted_zone(self.id)

    def get_nameservers(self):
        """ Get the list of nameservers for this zone."""
        for record in self.get_records():
            if record.type == 'NS':
                return record.resource_records


class Status(object):
    def __init__(self, change_dict):
        for key in change_dict:
            if key == 'Id':
                self.__setattr__(key.lower(), change_dict[key].replace('/change/',''))
            else:
                self.__setattr__(key.lower(), change_dict[key])
    def update(self):
        """ Update the status of this request."""
        status = route53.get_change(self.id)['GetChangeResponse']['ChangeInfo']['Status']
        self.status = status
        return status

    def __repr__(self):
        return '<Status:%s>' % self.status

