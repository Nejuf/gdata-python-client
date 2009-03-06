#!/usr/bin/env python
#
# Copyright (C) 2009 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# This module is used for version 2 of the Google Data APIs.
# These tests attempt to connect to Google servers.


__author__ = 'j.s@google.com (Jeff Scudder)'


import unittest
import gdata.gauth
import gdata.client
import atom.http_core
import atom.mock_http_core
# TODO: switch to using v2 atom data once it is available.
import atom
from gdata.test_config import settings


class BloggerTest(unittest.TestCase):

  def setUp(self):
    self.skip_tests = settings.RUN_LIVE_TESTS == False
    # Getting the auth token only needs to be done once in the course of test
    # runs, so this belongs in __init__ instead of setUp.
    if (not self.skip_tests 
        and settings.BLOGGER_CONFIG['auth_token'] is None):
      login_client = gdata.client.GDClient()
      # Obtain a client login token and use for all tests.
      settings.BLOGGER_CONFIG[
          'auth_token'] = login_client.request_client_login_token(
              settings.blogger_email(), 
              settings.blogger_password(), 'blogger',
              'BloggerTest client')
    if not self.skip_tests:
      self.client = gdata.client.GDClient()
      self.client.auth_token = settings.BLOGGER_CONFIG['auth_token']
      # Use a mock HTTP client which will record and replay the HTTP traffic
      # from these tests.
      self.client.http_client = atom.mock_http_core.MockHttpClient()

  def test_create_update_delete(self):
    if self.skip_tests:
      return

    # Either load the recording or prepare to make a live request.
    self.client.http_client._load_or_use_client(
        'live_client_test.BloggerTest.test_create_update_delete', 
        atom.http_core.HttpClient())

    blog_post = atom.Entry(
        title=atom.Title(text=settings.BLOGGER_CONFIG['title']),
        content=atom.Content(text=settings.BLOGGER_CONFIG['content']))
    http_request = atom.http_core.HttpRequest()
    http_request.add_body_part(str(blog_post), 'application/atom+xml')

    entry = self.client.request('POST', 
        'http://www.blogger.com/feeds/%s/posts/default' % (
            settings.BLOGGER_CONFIG['blog_id']),
         converter=atom.EntryFromString, http_request=http_request)

    self.assertEqual(entry.title.text, settings.BLOGGER_CONFIG['title'])
    self.assertEqual(entry.content.text, settings.BLOGGER_CONFIG['content'])

    # Delete the test entry from the blog.
    edit_link = None
    for link in entry.link:
      if link.rel == 'edit':
        edit_link = link.href
    response = self.client.request('DELETE', edit_link)
    self.assertEqual(response.status, 200)

    # If this was a live request, save the recording.
    if self.client.http_client.real_client is not None:
      self.client.http_client._save_recordings(
          'live_client_test.BloggerTest.test_create_update_delete')


def suite():
  return unittest.TestSuite((unittest.makeSuite(BloggerTest, 'test'),))


if __name__ == '__main__':
  unittest.main()
