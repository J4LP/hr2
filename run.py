#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from j4hr import main

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    main.app.run('0.0.0.0', port=port, debug=True)
