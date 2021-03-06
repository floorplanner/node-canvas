{
  'conditions': [
    ['OS=="win"', {
      'variables': {
        'GTK_Root%': 'C:/GTK', # Set the location of GTK all-in-one bundle
        'with_jpeg%': 'false',
        'with_gif%': 'false',
        'with_pango%': 'false',
        'with_freetype%': 'false',
        'variables': { # Nest jpeg_root to evaluate it before with_jpeg
          'jpeg_root%': '<!(node ./util/win_jpeg_lookup)'
        },
        'jpeg_root%': '<(jpeg_root)', # Take value of nested variable
        'conditions': [
          ['jpeg_root==""', {
            'with_jpeg%': 'false'
          }, {
            'with_jpeg%': 'true'
          }]
        ]
      }
    }, { # 'OS!="win"'
      'variables': {
        'with_jpeg%': '<!(./util/has_lib.sh jpeg)',
        'with_gif%': '<!(./util/has_lib.sh gif)',
        'with_pango%': '<!(./util/has_lib.sh pango)',
        'with_freetype%': '<!(./util/has_lib.sh freetype)'
      }
    }]
  ],
  'targets': [
    {
      'target_name': 'canvas-postbuild',
      'dependencies': ['canvas'],
      'conditions': [
        ['OS=="win"', {
          'copies': [{
            'destination': '<(PRODUCT_DIR)',
            'files': [
              '<(GTK_Root)/bin/libcairo-2.dll',
              '<(GTK_Root)/bin/libexpat-1.dll',
              '<(GTK_Root)/bin/libfontconfig-1.dll',
              '<(GTK_Root)/bin/libfreetype-6.dll',
              '<(GTK_Root)/bin/libpng14-14.dll',
              '<(GTK_Root)/bin/zlib1.dll',
            ]
          }]
        }]
      ]
    },
    {
      'target_name': 'canvas',
      'include_dirs': ["<!(node -e \"require('nan')\")"],
      'sources': [
        'src/Canvas.cc',
        'src/CanvasGradient.cc',
        'src/CanvasPattern.cc',
        'src/CanvasRenderingContext2d.cc',
        'src/color.cc',
        'src/Image.cc',
        'src/ImageData.cc',
        'src/init.cc'
      ],
      'conditions': [
        ['OS=="win"', {
          'libraries': [
            '-l<(GTK_Root)/lib/cairo.lib',
            '-l<(GTK_Root)/lib/libpng.lib'
          ],
          'include_dirs': [
            '<(GTK_Root)/include',
            '<(GTK_Root)/include/cairo',
          ],
          'defines': [
            '_USE_MATH_DEFINES' # for M_PI
          ],
          'configurations': {
            'Debug': {
              'msvs_settings': {
                'VCCLCompilerTool': {
                  'WarningLevel': 4,
                  'ExceptionHandling': 1,
                  'DisableSpecificWarnings': [4100, 4127, 4201, 4244, 4267, 4506, 4611, 4714, 4512]
                }
              }
            },
            'Release': {
              'msvs_settings': {
                'VCCLCompilerTool': {
                  'WarningLevel': 4,
                  'ExceptionHandling': 1,
                  'DisableSpecificWarnings': [4100, 4127, 4201, 4244, 4267, 4506, 4611, 4714, 4512]
                }
              }
            }
          }
        }, { # 'OS!="win"'
          'libraries': [
            '<!@(pkg-config pixman-1 --libs)',
            '<!@(pkg-config cairo --libs)',
            '<!@(pkg-config libpng --libs)'
          ],
          'include_dirs': [
            '<!@(pkg-config cairo --cflags-only-I | sed s/-I//g)',
            '<!@(pkg-config libpng --cflags-only-I | sed s/-I//g)'
          ]
        }],
        ['with_freetype=="true"', {
          'defines': [
            'HAVE_FREETYPE'
          ],
          'sources': [
            'src/FontFace.cc'
          ],
          'conditions': [
            ['OS=="win"', {
              # No support for windows right now.
            }, { # 'OS!="win"'
              'include_dirs': [ # tried to pass through cflags but failed.
                # Need to include the header files of cairo AND freetype.
                # Looking up the includes of cairo does both.
                '<!@(pkg-config cairo --cflags-only-I | sed s/-I//g)'
              ]
            }]
          ]
        }],
        ['with_pango=="true"', {
          'defines': [
            'HAVE_PANGO'
          ],
          'conditions': [
            ['OS=="win"', {
              'libraries': [
                '-l<(GTK_Root)/lib/pangocairo.lib'
              ]
            }, { # 'OS!="win"'
              'include_dirs': [ # tried to pass through cflags but failed
                '<!@(pkg-config pangocairo --cflags-only-I | sed s/-I//g)'
              ],
              'libraries': [
                '<!@(pkg-config pangocairo --libs)'
              ]
            }]
          ]
        }],
        ['with_jpeg=="true"', {
          'defines': [
            'HAVE_JPEG'
          ],
          'conditions': [
            ['OS=="win"', {
              'copies': [{
                'destination': '<(PRODUCT_DIR)',
                'files': [
                  '<(jpeg_root)/bin/jpeg62.dll',
                ]
              }],
              'include_dirs': [
                '<(jpeg_root)/include'
              ],
              'libraries': [
                '-l<(jpeg_root)/lib/jpeg.lib',
              ]
            }, {
              'libraries': [
                '-ljpeg'
              ]
            }]
          ]
        }],
        ['with_gif=="true"', {
          'defines': [
            'HAVE_GIF'
          ],
          'conditions': [
            ['OS=="win"', {
              'libraries': [
                '-l<(GTK_Root)/lib/gif.lib'
              ]
            }, {
              'libraries': [
                '-lgif'
              ]
            }]
          ]
        }]
      ]
    }
  ]
}
