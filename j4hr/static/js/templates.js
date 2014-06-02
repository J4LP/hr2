angular.module('hrApp').run(['$templateCache', function($templateCache) {
  'use strict';

  $templateCache.put('templates/angular/api_input.html',
    "<div class=\"row\">\n" +
    "    <div class=\"col-md-12\">\n" +
    "        <div class=\"progress\">\n" +
    "            <div class=\"progress-bar\" style=\"width: 20%\">Progress: 20%</div>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "    <div class=\"col-md-12\">\n" +
    "        <h2 class=\"subline\">API Key</h2>\n" +
    "        <p>For security reasons, we will ask and check for access to your mail, wallet transactions and other auditing data.</p>\n" +
    "        <p>We will not share it with peers.</p>\n" +
    "        <p>Please note that daily checks are in place and your access will be revoked if the system locates an incorrect API or at the discretion of the Alliance Leadership.</p>\n" +
    "    </div>\n" +
    "    <div class=\"col-md-12 text-center\">\n" +
    "        <h4><a href=\"https://community.eveonline.com/support/api-key/CreatePredefined?accessMask=65544538\" target=\"_blank\">Generate an API Key here, without an EXPIRY set</a></h4>\n" +
    "    </div>\n" +
    "    <div class=\"col-md-12\">\n" +
    "        <form name=\"apiForm\" class=\"form-horizontal col-md-8 col-md-offset-2 api-form\" ng-submit=\"checkApiKey()\" novalidate>\n" +
    "            <div class=\"form-group\" ng-class=\"{'has-error': apiForm.uKey_id.$dirty && apiForm.uKey_id.$invalid}\">\n" +
    "                <label for=\"key_id\" class=\"col-sm-2 control-label\">Key ID</label>\n" +
    "                <div class=\"col-sm-10\">\n" +
    "                    <div class=\"input-group\">\n" +
    "                        <span class=\"input-group-addon\"><i class=\"fa fa-key\"></i></span>\n" +
    "                        <input type=\"text\" ng-model=\"key_id\" class=\"form-control\" id=\"uKey_id\" name=\"uKey_id\" placeholder=\"Your Key ID\" required>\n" +
    "                    </div>\n" +
    "                    <div ng-show=\"apiForm.uKey_id.$dirty && apiForm.uKey_id.$invalid\">\n" +
    "                        <span class=\"help-block\" ng-show=\"apiForm.uKey_id.$error.required\">Key ID missing.</span>\n" +
    "                    </div>\n" +
    "                </div>\n" +
    "            </div>\n" +
    "            <div class=\"form-group\" ng-class=\"{'has-error': apiForm.uVcode.$dirty && apiForm.uVcode.$invalid}\">\n" +
    "                <label for=\"vcode\" class=\"col-sm-2 control-label\">vCode</label>\n" +
    "                <div class=\"col-sm-10\">\n" +
    "                    <div class=\"input-group\">\n" +
    "                        <span class=\"input-group-addon\"><i class=\"fa fa-lock\"></i></span>\n" +
    "                        <input type=\"text\" ng-model=\"vcode\" class=\"form-control\" id=\"uVcode\" name=\"uVcode\" placeholder=\"Your Vcode\" required>\n" +
    "                    </div>\n" +
    "                    <div ng-show=\"apiForm.uVcode.$dirty && apiForm.uVcode.$invalid\">\n" +
    "                        <span class=\"help-block\" ng-show=\"apiForm.uVcode.$error.required\">vCode missing.</span>\n" +
    "                    </div>\n" +
    "                </div>\n" +
    "            </div>\n" +
    "            <div class=\"form-group\">\n" +
    "                <div class=\"col-sm-offset-2 col-sm-10\">\n" +
    "                    <button class=\"btn btn-success btn-block\" type=\"submit\"><i class=\"fa fa-check\"></i> Submit</button>\n" +
    "                </div>\n" +
    "            </div>\n" +
    "        </form>\n" +
    "    </div>\n" +
    "</div>\n"
  );


  $templateCache.put('templates/angular/characters.html',
    "<div class=\"row\">\n" +
    "    <div class=\"col-md-11\">\n" +
    "        <div class=\"progress\">\n" +
    "            <div class=\"progress-bar\" style=\"width: 40%\">Progress: 40%</div>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "    <div class=\"col-md-1\">\n" +
    "        <a ng-href=\"/apply/reset\" class=\"btn btn-warning btn-xs btn-block\">Reset</a>\n" +
    "    </div>\n" +
    "</div>\n" +
    "<div class=\"row\">\n" +
    "    <div class=\"col-md-12\">\n" +
    "        <h2 class=\"subline\">Characters <small>Choose one</small></h2>\n" +
    "        <div class=\"row\" ng-show=\"!characters.length\">\n" +
    "            <div class=\"col-md-12\">\n" +
    "                <div class=\"spinner\">\n" +
    "                    <div class=\"rect1\"></div>\n" +
    "                    <div class=\"rect2\"></div>\n" +
    "                    <div class=\"rect3\"></div>\n" +
    "                    <div class=\"rect4\"></div>\n" +
    "                    <div class=\"rect5\"></div>\n" +
    "                </div>\n" +
    "            </div>\n" +
    "        </div>\n" +
    "        <div class=\"row\">\n" +
    "            <div class=\"col-md-4\" ng-repeat=\"character in characters\">\n" +
    "                <div class=\"thumbnail character\">\n" +
    "                    <img ng-src=\"https://image.eveonline.com/Character/{[{character.characterID}]}_512.jpg\" alt=\"{[{character.characterName}]}\">\n" +
    "                    <div class=\"caption\">\n" +
    "                        <h4>{[{character.characterName}]}</h4>\n" +
    "                        <dl>\n" +
    "                            <dt>Corporation</dt>\n" +
    "                            <dd>{[{character.corporation}]}</dd>\n" +
    "                            <dt>Alliance</dt>\n" +
    "                            <dd ng-show=\"character.alliance.length\">{[{character.alliance}]}</dd>\n" +
    "                            <dd ng-show=\"!character.alliance.length\">No alliance</dd>\n" +
    "                        </dl>\n" +
    "                        <a href ng-click=\"pick(character.characterID)\" class=\"btn btn-block btn-success\"><i class=\"fa fa-check\"></i> Choose</a>\n" +
    "                    </div>\n" +
    "                </div>\n" +
    "            </div>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "</div>\n"
  );


  $templateCache.put('templates/angular/corporations.html',
    "<div class=\"row\">\n" +
    "    <div class=\"col-md-11\">\n" +
    "        <div class=\"progress\">\n" +
    "            <div class=\"progress-bar\" style=\"width: 60%\">Progress: 60%</div>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "    <div class=\"col-md-1\">\n" +
    "        <a ng-href=\"/apply/reset\" class=\"btn btn-warning btn-xs btn-block\">Reset</a>\n" +
    "    </div>\n" +
    "</div>\n" +
    "\n" +
    "<div class=\"row\">\n" +
    "    <div class=\"col-md-12\">\n" +
    "        <h2 class=\"subline\">Corporations <small>Apply now !</small></h2>\n" +
    "    </div>\n" +
    "</div>\n" +
    "\n" +
    "<div class=\"row\">\n" +
    "    <div class=\"col-md-2\" ng-repeat=\"corporation in corporations\">\n" +
    "        <div class=\"thumbnail corporation\">\n" +
    "            <img ng-src=\"https://image.eveonline.com/Corporation/{[{corporation.id}]}_256.png\" alt=\"{[{corporation.name}]}\">\n" +
    "            <div class=\"caption\">\n" +
    "                <h5>{[{corporation.name}]}</h5>\n" +
    "                <a ng-click=\"pick(corporation.id)\" class=\"btn btn-sm btn-primary btn-block\" ><i class=\"fa fa-check\"></i> Apply</a>\n" +
    "            </div>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "</div>\n"
  );


  $templateCache.put('templates/angular/denied.html',
    "<div class=\"row\">\n" +
    "    <div class=\"col-md-11\">\n" +
    "        <div class=\"progress\">\n" +
    "            <div class=\"progress-bar progress-bar-danger\" style=\"width: 100%\">Progress: 100%</div>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "    <div class=\"col-md-1\">\n" +
    "        <a ng-href=\"/apply/reset\" class=\"btn btn-warning btn-xs btn-block\">Reset</a>\n" +
    "    </div>\n" +
    "</div>\n" +
    "<div class=\"row\">\n" +
    "    <div class=\"col-md-12\">\n" +
    "        <h2 class=\"subline\">Application denied</h2>\n" +
    "        <div class=\"alert alert-danger\">\n" +
    "            <p>Sorry but it appears that one or multiple characters retrieved from your API Key is already belonging to one of our corporations ! You do not need to apply.</p>\n" +
    "            <p>If you are trying to apply for one of your alternate characters, please add directly your API Key on your Auth account.</p>\n" +
    "            <p>Otherwise, feel free to contact one of our HR person if you have any questions.</p>\n" +
    "        </div>\n" +
    "        <div class=\"text-center\">\n" +
    "            <h3>\n" +
    "                <a href=\"#\">Back to Auth</a>\n" +
    "            </h3>\n" +
    "        </div>\n" +
    "\n" +
    "    </div>\n" +
    "</div>\n"
  );


  $templateCache.put('templates/angular/done.html',
    "<div class=\"row\">\n" +
    "    <div class=\"col-md-11\">\n" +
    "        <div class=\"progress\">\n" +
    "            <div class=\"progress-bar progress-bar-success\" style=\"width: 100%\">Progress: 100%</div>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "</div>\n" +
    "<div class=\"row\">\n" +
    "    <div class=\"col-md-12\">\n" +
    "        <h2 class=\"subline\">Application received !</h2>\n" +
    "        <div class=\"alert alert-success\">\n" +
    "            <p>Congratulations ! Your application has been received and will be reviewed very soon !</p>\n" +
    "            <p>You will receive an email with further informations once your application has been reviewed.</p>\n" +
    "        </div>\n" +
    "        <div class=\"text-center\">\n" +
    "            <h3>\n" +
    "                <a href=\"/\" target=\"_self\">Back to J4LP</a>\n" +
    "            </h3>\n" +
    "        </div>\n" +
    "\n" +
    "    </div>\n" +
    "</div>\n"
  );


  $templateCache.put('templates/angular/recap.html',
    "<div class=\"row\">\n" +
    "    <div class=\"col-md-11\">\n" +
    "        <div class=\"progress\">\n" +
    "            <div class=\"progress-bar\" style=\"width: 90%\">Progress: 90%</div>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "    <div class=\"col-md-1\">\n" +
    "        <a ng-href=\"/apply/reset\" class=\"btn btn-warning btn-xs btn-block\">Reset</a>\n" +
    "    </div>\n" +
    "</div>\n" +
    "\n" +
    "<div class=\"row\">\n" +
    "    <div class=\"col-md-12\">\n" +
    "        <h2 class=\"subline\">Recap <small>Is everything correct ?</small></h2>\n" +
    "    </div>\n" +
    "</div>\n" +
    "\n" +
    "<div class=\"row\">\n" +
    "    <div class=\"col-md-6 col-md-offset-3 recap-illustrations\">\n" +
    "        <img ng-src=\"https://image.eveonline.com/Character/{[{app.getInt('characterID')}]}_256.jpg\" alt=\"\" class=\"thumbnail\">\n" +
    "        <i class=\"fa fa-arrow-right fa-3x\"></i>\n" +
    "        <img ng-src=\"https://image.eveonline.com/Corporation/{[{app.getInt('corporationID')}]}_256.png\" alt=\"\" class=\"thumbnail\">\n" +
    "    </div>\n" +
    "    <div class=\"col-md-6 col-md-offset-3\">\n" +
    "        <dl class=\"dl-horizontal text-center\">\n" +
    "            <dt>Applicant</dt>\n" +
    "            <dd>{[{app.get('characterName')}]}</dd>\n" +
    "            <dt>Corporation</dt>\n" +
    "            <dd>{[{app.get('corporationName')}]}</dd>\n" +
    "            <dt>Alliance</dt>\n" +
    "            <dd>I Whip My Slaves Back and Forth</dd>\n" +
    "            <div ng-show=\"app.get('redditUsername')\">\n" +
    "                <dt>Reddit Username</dt>\n" +
    "                <dd>{[{app.get('redditUsername')}]}</dd>\n" +
    "            </div>\n" +
    "        </dl>\n" +
    "        <h3 class=\"subline\">Email</h3>\n" +
    "        <p>Make sure this email is valid as we will need it to contact you when your application is reviewed.</p>\n" +
    "        <input ng-model=\"email\" type=\"email\" class=\"form-control\" name=\"email\" id=\"email\" placeholder=\"Email\">\n" +
    "        <h3 class=\"subline\">Motivation</h3>\n" +
    "        <p>Please write below why you wish to join us, who do you know, who could recommend you, etc...</p>\n" +
    "        <textarea ng-model=\"motivation\" class=\"form-control\" name=\"motivation\" id=\"motivation\" rows=\"3\"></textarea>\n" +
    "        <br>\n" +
    "        <a ng-click=\"apply()\" class=\"btn btn-block btn-lg btn-success\"><i class=\"fa fa-envelope\"></i> Send application</a>\n" +
    "        <br>\n" +
    "    </div>\n" +
    "</div>\n"
  );

}]);
