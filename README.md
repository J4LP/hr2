Human Resources for your Eve Online alliance
============================================

**This is a work in progress that needs a bit of setup to make it work correctly**

## Instructions

    # Clone the repository and create a new virtual environment
    git clone https://github.com/J4LP/newauth
    virtualenv .
    pip install -r requirements.txt
    # Edit the settings
    cp j4hr/settings_dist.py j4hr/settings.py
    # Get the assets with Bower
    bower install
    # Build the assets
    python manage.py assets build
    # Build the corporation list and outposts
    python manage.py update_corporations
    python manage.py update_outposts
    # Launch HR2
    python run.py
    # For production, set J4HR2_ENV='prod'.

## Preview

![Imgur](http://i.imgur.com/W4f7Hif.png)

## TODO

- [ ] Clean the assets system
- [ ] Emails
- [ ] NewAuth link
- [ ] Admin statistics
- [ ] Tests

## Dependencies

This project depends on MongoDB for storing applications and reports and use J4OAuth for the authentication backend.

## Contributing

Pull requests are most welcomed, but please come talk to us before at asylum@public.conference.talkinlocal.org (XMPP) to see what we're up to !

## License

The MIT License (MIT)

Copyright (c) 2014 @adrien-f

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


