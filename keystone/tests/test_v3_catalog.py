# Copyright 2013 OpenStack Foundation
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import copy
import uuid

from keystone.tests import test_v3


class CatalogTestCase(test_v3.RestfulTestCase):
    """Test service & endpoint CRUD."""

    # region crud tests

    def test_create_region_with_id(self):
        """Call ``PUT /regions/{region_id}`` w/o an ID in the request body."""
        ref = self.new_region_ref()
        region_id = ref.pop('id')
        r = self.put(
            '/regions/%s' % region_id,
            body={'region': ref},
            expected_status=201)
        self.assertValidRegionResponse(r, ref)
        # Double-check that the region ID was kept as-is and not
        # populated with a UUID, as is the case with POST /v3/regions
        self.assertEqual(region_id, r.json['region']['id'])

    def test_create_region_with_matching_ids(self):
        """Call ``PUT /regions/{region_id}`` with an ID in the request body."""
        ref = self.new_region_ref()
        region_id = ref['id']
        r = self.put(
            '/regions/%s' % region_id,
            body={'region': ref},
            expected_status=201)
        self.assertValidRegionResponse(r, ref)
        # Double-check that the region ID was kept as-is and not
        # populated with a UUID, as is the case with POST /v3/regions
        self.assertEqual(region_id, r.json['region']['id'])

    def test_create_region(self):
        """Call ``POST /regions`` with an ID in the request body."""
        # the ref will have an ID defined on it
        ref = self.new_region_ref()
        r = self.post(
            '/regions',
            body={'region': ref})
        self.assertValidRegionResponse(r, ref)

        # we should be able to get the region, having defined the ID ourselves
        r = self.get(
            '/regions/%(region_id)s' % {
                'region_id': ref['id']})
        self.assertValidRegionResponse(r, ref)

    def test_create_region_without_id(self):
        """Call ``POST /regions`` without an ID in the request body."""
        ref = self.new_region_ref()

        # instead of defining the ID ourselves...
        del ref['id']

        # let the service define the ID
        r = self.post(
            '/regions',
            body={'region': ref},
            expected_status=201)
        self.assertValidRegionResponse(r, ref)

    def test_create_region_with_conflicting_ids(self):
        """Call ``PUT /regions/{region_id}`` with conflicting region IDs."""
        # the region ref is created with an ID
        ref = self.new_region_ref()

        # but instead of using that ID, make up a new, conflicting one
        self.put(
            '/regions/%s' % uuid.uuid4().hex,
            body={'region': ref},
            expected_status=400)

    def test_list_regions(self):
        """Call ``GET /regions``."""
        r = self.get('/regions')
        self.assertValidRegionListResponse(r, ref=self.region)

    def test_list_regions_xml(self):
        """Call ``GET /regions (xml data)``."""
        r = self.get('/regions', content_type='xml')
        self.assertValidRegionListResponse(r, ref=self.region)

    def test_get_region(self):
        """Call ``GET /regions/{region_id}``."""
        r = self.get('/regions/%(region_id)s' % {
            'region_id': self.region_id})
        self.assertValidRegionResponse(r, self.region)

    def test_update_region(self):
        """Call ``PATCH /regions/{region_id}``."""
        region = self.new_region_ref()
        del region['id']
        r = self.patch('/regions/%(region_id)s' % {
            'region_id': self.region_id},
            body={'region': region})
        self.assertValidRegionResponse(r, region)

    def test_delete_region(self):
        """Call ``DELETE /regions/{region_id}``."""
        self.delete('/regions/%(region_id)s' % {
            'region_id': self.region_id})

    # service crud tests

    def test_create_service(self):
        """Call ``POST /services``."""
        ref = self.new_service_ref()
        r = self.post(
            '/services',
            body={'service': ref})
        self.assertValidServiceResponse(r, ref)

    def test_list_services(self):
        """Call ``GET /services``."""
        r = self.get('/services')
        self.assertValidServiceListResponse(r, ref=self.service)

    def test_list_services_xml(self):
        """Call ``GET /services (xml data)``."""
        r = self.get('/services', content_type='xml')
        self.assertValidServiceListResponse(r, ref=self.service)

    def test_get_service(self):
        """Call ``GET /services/{service_id}``."""
        r = self.get('/services/%(service_id)s' % {
            'service_id': self.service_id})
        self.assertValidServiceResponse(r, self.service)

    def test_update_service(self):
        """Call ``PATCH /services/{service_id}``."""
        service = self.new_service_ref()
        del service['id']
        r = self.patch('/services/%(service_id)s' % {
            'service_id': self.service_id},
            body={'service': service})
        self.assertValidServiceResponse(r, service)

    def test_delete_service(self):
        """Call ``DELETE /services/{service_id}``."""
        self.delete('/services/%(service_id)s' % {
            'service_id': self.service_id})

    # endpoint crud tests

    def test_list_endpoints(self):
        """Call ``GET /endpoints``."""
        r = self.get('/endpoints')
        # FIXME(blk-u): Endpoints should default to enabled=True, so should be
        # able to remove keys_to_check=, see bug 1282266.
        self.assertValidEndpointListResponse(r, ref=self.endpoint,
                                             keys_to_check=['name',
                                                            'description'])

    def test_list_endpoints_xml(self):
        """Call ``GET /endpoints`` (xml data)."""
        r = self.get('/endpoints', content_type='xml')
        # FIXME(blk-u): Endpoints should default to enabled=True, so should be
        # able to remove keys_to_check=, see bug 1282266.
        self.assertValidEndpointListResponse(r, ref=self.endpoint,
                                             keys_to_check=['name',
                                                            'description'])

    def test_create_endpoint_no_enabled(self):
        """Call ``POST /endpoints``."""
        ref = self.new_endpoint_ref(service_id=self.service_id)
        r = self.post(
            '/endpoints',
            body={'endpoint': ref})
        # FIXME(blk-u): Endpoints should default to enabled=True, so should be
        # able to remove keys_to_check=, see bug 1282266, and also should be
        # able to assertIs(True, r.result['endpoint']['enabled'] on the next
        # line.
        self.assertValidEndpointResponse(r, ref, keys_to_check=['name',
                                                                'description'])
        self.assertFalse('enabled' in r.result['endpoint'])

    def test_create_endpoint_enabled_true(self):
        """Call ``POST /endpoints`` with enabled: true."""
        ref = self.new_endpoint_ref(service_id=self.service_id,
                                    enabled=True)
        r = self.post(
            '/endpoints',
            body={'endpoint': ref})
        self.assertValidEndpointResponse(r, ref)
        self.assertIs(True, r.result['endpoint']['enabled'])

    def test_create_endpoint_enabled_false(self):
        """Call ``POST /endpoints`` with enabled: false."""
        ref = self.new_endpoint_ref(service_id=self.service_id,
                                    enabled=False)
        r = self.post(
            '/endpoints',
            body={'endpoint': ref})
        self.assertValidEndpointResponse(r, ref)
        self.assertIs(False, r.result['endpoint']['enabled'])

    def test_create_endpoint_enabled_str_true(self):
        """Call ``POST /endpoints`` with enabled: 'True'."""
        ref = self.new_endpoint_ref(service_id=self.service_id,
                                    enabled='True')
        # FIXME(blk-u): The enabled field is defined as a Boolean, so
        # a string should be rejected with 400 Bad Request, see bug 1282266.
        r = self.post(
            '/endpoints',
            body={'endpoint': ref})
        self.assertValidEndpointResponse(r, ref)
        self.assertEqual('True', r.result['endpoint']['enabled'])

    def test_create_endpoint_enabled_str_false(self):
        """Call ``POST /endpoints`` with enabled: 'False'."""
        ref = self.new_endpoint_ref(service_id=self.service_id,
                                    enabled='False')
        # FIXME(blk-u): The enabled field is defined as a Boolean, so
        # a string should be rejected with 400 Bad Request, see bug 1282266.
        r = self.post(
            '/endpoints',
            body={'endpoint': ref})
        self.assertValidEndpointResponse(r, ref)
        self.assertEqual('False', r.result['endpoint']['enabled'])

    def test_create_endpoint_enabled_str_random(self):
        """Call ``POST /endpoints`` with enabled: 'puppies'."""
        ref = self.new_endpoint_ref(service_id=self.service_id,
                                    enabled='puppies')
        # FIXME(blk-u): The enabled field is defined as a Boolean, so
        # a string should be rejected with 400 Bad Request, see bug 1282266.
        r = self.post(
            '/endpoints',
            body={'endpoint': ref})
        self.assertValidEndpointResponse(r, ref)
        self.assertEqual('puppies', r.result['endpoint']['enabled'])

    def assertValidErrorResponse(self, response):
        self.assertTrue(response.status_code in [400])

    def test_create_endpoint_400(self):
        """Call ``POST /endpoints``."""
        ref = self.new_endpoint_ref(service_id=self.service_id)
        ref["region"] = "0" * 256
        self.post('/endpoints', body={'endpoint': ref}, expected_status=400)

    def test_get_endpoint(self):
        """Call ``GET /endpoints/{endpoint_id}``."""
        r = self.get(
            '/endpoints/%(endpoint_id)s' % {
                'endpoint_id': self.endpoint_id})
        self.assertValidEndpointResponse(r, self.endpoint)

    def test_update_endpoint(self):
        """Call ``PATCH /endpoints/{endpoint_id}``."""
        # FIXME(blk-u): Endpoints should default to enabled=True, so should be
        # able to remove enabled=, see bug 1282266. Also, should be able to
        # self.assertIs(True, r.result['endpoint']['enabled']).
        ref = self.new_endpoint_ref(service_id=self.service_id, enabled=True)
        del ref['id']
        r = self.patch(
            '/endpoints/%(endpoint_id)s' % {
                'endpoint_id': self.endpoint_id},
            body={'endpoint': ref})
        self.assertValidEndpointResponse(r, ref)

    def test_update_endpoint_enabled_true(self):
        """Call ``PATCH /endpoints/{endpoint_id}`` with enabled: True."""
        r = self.patch(
            '/endpoints/%(endpoint_id)s' % {
                'endpoint_id': self.endpoint_id},
            body={'endpoint': {'enabled': True}})
        self.assertValidEndpointResponse(r, self.endpoint)
        self.assertIs(True, r.result['endpoint']['enabled'])

    def test_update_endpoint_enabled_false(self):
        """Call ``PATCH /endpoints/{endpoint_id}`` with enabled: False."""
        r = self.patch(
            '/endpoints/%(endpoint_id)s' % {
                'endpoint_id': self.endpoint_id},
            body={'endpoint': {'enabled': False}})
        exp_endpoint = copy.copy(self.endpoint)
        exp_endpoint['enabled'] = False
        self.assertValidEndpointResponse(r, exp_endpoint)
        self.assertIs(False, r.result['endpoint']['enabled'])

    def test_update_endpoint_enabled_str_true(self):
        """Call ``PATCH /endpoints/{endpoint_id}`` with enabled: 'True'."""
        # FIXME(blk-u): Enabled is a boolean so setting it to a string should
        # fail with 400 Bad Request, see bug 1282266.
        r = self.patch(
            '/endpoints/%(endpoint_id)s' % {
                'endpoint_id': self.endpoint_id},
            body={'endpoint': {'enabled': 'True'}})
        exp_endpoint = copy.copy(self.endpoint)
        exp_endpoint['enabled'] = 'True'
        self.assertValidEndpointResponse(r, exp_endpoint)

    def test_update_endpoint_enabled_str_false(self):
        """Call ``PATCH /endpoints/{endpoint_id}`` with enabled: 'False'."""
        # FIXME(blk-u): Enabled is a boolean so setting it to a string should
        # fail with 400 Bad Request, see bug 1282266.
        r = self.patch(
            '/endpoints/%(endpoint_id)s' % {
                'endpoint_id': self.endpoint_id},
            body={'endpoint': {'enabled': 'False'}})
        exp_endpoint = copy.copy(self.endpoint)
        exp_endpoint['enabled'] = 'False'
        self.assertValidEndpointResponse(r, exp_endpoint)

    def test_update_endpoint_enabled_str_random(self):
        """Call ``PATCH /endpoints/{endpoint_id}`` with enabled: 'kitties'."""
        # FIXME(blk-u): Enabled is a boolean so setting it to a string should
        # fail with 400 Bad Request, see bug 1282266.
        r = self.patch(
            '/endpoints/%(endpoint_id)s' % {
                'endpoint_id': self.endpoint_id},
            body={'endpoint': {'enabled': 'kitties'}})
        exp_endpoint = copy.copy(self.endpoint)
        exp_endpoint['enabled'] = 'kitties'
        self.assertValidEndpointResponse(r, exp_endpoint)

    def test_delete_endpoint(self):
        """Call ``DELETE /endpoints/{endpoint_id}``."""
        self.delete(
            '/endpoints/%(endpoint_id)s' % {
                'endpoint_id': self.endpoint_id})

    def test_create_endpoint_on_v2(self):
        # clear the v3 endpoint so we only have endpoints created on v2
        self.delete(
            '/endpoints/%(endpoint_id)s' % {
                'endpoint_id': self.endpoint_id})

        # create a v3 endpoint ref, and then tweak it back to a v2-style ref
        # FIXME(blk-u): Should be able to remove enabled=True since it should
        # be optional, see bug 1282266.
        ref = self.new_endpoint_ref(service_id=self.service['id'],
                                    enabled=True)
        del ref['id']
        del ref['interface']
        ref['publicurl'] = ref.pop('url')
        ref['internalurl'] = None
        # don't set adminurl to ensure it's absence is handled like internalurl

        # create the endpoint on v2 (using a v3 token)
        r = self.admin_request(
            method='POST',
            path='/v2.0/endpoints',
            token=self.get_scoped_token(),
            body={'endpoint': ref})
        endpoint_v2 = r.result['endpoint']

        # test the endpoint on v3
        r = self.get('/endpoints')
        endpoints = self.assertValidEndpointListResponse(r)
        self.assertEqual(len(endpoints), 1)
        endpoint_v3 = endpoints.pop()

        # these attributes are identical between both API's
        self.assertEqual(endpoint_v3['region'], ref['region'])
        self.assertEqual(endpoint_v3['service_id'], ref['service_id'])
        self.assertEqual(endpoint_v3['description'], ref['description'])

        # a v2 endpoint is not quite the same concept as a v3 endpoint, so they
        # receive different identifiers
        self.assertNotEqual(endpoint_v2['id'], endpoint_v3['id'])

        # v2 has a publicurl; v3 has a url + interface type
        self.assertEqual(endpoint_v3['url'], ref['publicurl'])
        self.assertEqual(endpoint_v3['interface'], 'public')

        # tests for bug 1152632 -- these attributes were being returned by v3
        self.assertNotIn('publicurl', endpoint_v3)
        self.assertNotIn('adminurl', endpoint_v3)
        self.assertNotIn('internalurl', endpoint_v3)

        # test for bug 1152635 -- this attribute was being returned by v3
        self.assertNotIn('legacy_endpoint_id', endpoint_v3)
