import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import pandas as pd

def send_email(recipient_email, podcast_title, description_file_path, podcast_file_path, podcast_num):
    # Email Configuration
    sender_email = 
    sender_password =  # Use an app-specific password if needed
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # parse podcast_description df
    podcast_description = pd.read_csv(description_file_path)
    title_1 = podcast_description.iloc[0]['title']
    description_1 = podcast_description.iloc[0]['description']
    url_1 = podcast_description.iloc[0]['url']
    title_2 = podcast_description.iloc[1]['title']
    description_2 = podcast_description.iloc[1]['description']
    url_2 = podcast_description.iloc[1]['url']
    title_3 = podcast_description.iloc[2]['title']
    description_3 = podcast_description.iloc[2]['description']
    url_3 = podcast_description.iloc[2]['url']
    title_4 = podcast_description.iloc[3]['title']
    description_4 = podcast_description.iloc[3]['description']
    url_4 = podcast_description.iloc[3]['url']
    title_5 = podcast_description.iloc[4]['title']
    description_5 = podcast_description.iloc[4]['description']
    url_5 = podcast_description.iloc[4]['url']


    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"Episode {podcast_num} of Astra is here!"  # Email Subject

    # Email Body (HTML)
    email_body = f"""

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" lang="en">
<head>
<title></title>
<meta charset="UTF-8" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<!--[if !mso]>-->
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<!--<![endif]-->
<meta name="x-apple-disable-message-reformatting" content="" />
<meta content="target-densitydpi=device-dpi" name="viewport" />
<meta content="true" name="HandheldFriendly" />
<meta content="width=device-width" name="viewport" />
<meta name="format-detection" content="telephone=no, date=no, address=no, email=no, url=no" />
<style type="text/css">
table {{
border-collapse: separate;
table-layout: fixed;
mso-table-lspace: 0pt;
mso-table-rspace: 0pt
}}
table td {{
border-collapse: collapse
}}
.ExternalClass {{
width: 100%
}}
.ExternalClass,
.ExternalClass p,
.ExternalClass span,
.ExternalClass font,
.ExternalClass td,
.ExternalClass div {{
line-height: 100%
}}
body, a, li, p, h1, h2, h3 {{
-ms-text-size-adjust: 100%;
-webkit-text-size-adjust: 100%;
}}
html {{
-webkit-text-size-adjust: none !important
}}
body, #innerTable {{
-webkit-font-smoothing: antialiased;
-moz-osx-font-smoothing: grayscale
}}
#innerTable img+div {{
display: none;
display: none !important
}}
img {{
Margin: 0;
padding: 0;
-ms-interpolation-mode: bicubic
}}
h1, h2, h3, p, a {{
line-height: inherit;
overflow-wrap: normal;
white-space: normal;
word-break: break-word
}}
a {{
text-decoration: none
}}
h1, h2, h3, p {{
min-width: 100%!important;
width: 100%!important;
max-width: 100%!important;
display: inline-block!important;
border: 0;
padding: 0;
margin: 0
}}
a[x-apple-data-detectors] {{
color: inherit !important;
text-decoration: none !important;
font-size: inherit !important;
font-family: inherit !important;
font-weight: inherit !important;
line-height: inherit !important
}}
u + #body a {{
color: inherit;
text-decoration: none;
font-size: inherit;
font-family: inherit;
font-weight: inherit;
line-height: inherit;
}}
a[href^="mailto"],
a[href^="tel"],
a[href^="sms"] {{
color: inherit;
text-decoration: none
}}
</style>
<style type="text/css">
@media (min-width: 481px) {{
.hd {{ display: none!important }}
}}
</style>
<style type="text/css">
@media (max-width: 480px) {{
.hm {{ display: none!important }}
}}
</style>
<style type="text/css">
@media (max-width: 480px) {{
.t147,.t29{{padding:32px!important}}.t149,.t192,.t31{{width:480px!important}}.t23,.t28{{Margin-left:0px!important}}.t104,.t110,.t122,.t127,.t133,.t145,.t16,.t175,.t182,.t188,.t22,.t27,.t36,.t42,.t53,.t64,.t76,.t81,.t87,.t99{{width:416px!important}}.t114,.t137,.t46,.t68,.t91{{vertical-align:top!important;width:600px!important}}.t155,.t168{{vertical-align:middle!important}}.t10,.t115,.t138,.t47,.t69,.t92{{text-align:left!important}}.t190{{padding-left:32px!important;padding-right:32px!important}}.t169,.t172{{text-align:center!important}}.t168{{width:800px!important}}.t153,.t2{{display:revert!important}}.t155{{width:50px!important}}.t4,.t9{{vertical-align:top!important}}.t159{{width:366px!important}}.t4{{width:65px!important}}.t9{{width:auto!important;max-width:100%!important}}
}}
</style>

<!--[if !mso]>-->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&amp;family=Lato:wght@400;700&amp;display=swap" rel="stylesheet" type="text/css" />
<!--<![endif]-->
<!--[if mso]>
<xml>
<o:OfficeDocumentSettings>
<o:AllowPNG/>
<o:PixelsPerInch>96</o:PixelsPerInch>
</o:OfficeDocumentSettings>
</xml>
<![endif]-->
</head>
<body id="body" class="t196" style="min-width:100%;Margin:0px;padding:0px;background-color:#F8F7FD;"><div class="t195" style="background-color:#F8F7FD;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" align="center"><tr><td class="t194" style="font-size:0;line-height:0;mso-line-height-rule:exactly;background-color:#F8F7FD;" valign="top" align="center">
<!--[if mso]>
<v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false">
<v:fill color="#F8F7FD"/>
</v:background>
<![endif]-->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" align="center" id="innerTable"><tr><td align="center">
<table class="t32" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="600" class="t31" style="background-color:#003238;width:600px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t31" style="background-color:#003238;width:600px;">
<!--<![endif]-->
<table class="t30" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t29" style="padding:40px 48px 40px 48px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100% !important;"><tr><td align="center">
<table class="t17" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="504" class="t16" style="width:504px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t16" style="width:504px;">
<!--<![endif]-->
<table class="t15" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t14" style="padding:20px 15px 20px 15px;"><div class="t13" style="width:100%;text-align:left;"><div class="t12" style="display:inline-block;"><table class="t11" role="presentation" cellpadding="0" cellspacing="0" align="left" valign="top">
<tr class="t10"><td></td><td class="t4" width="65" valign="top">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="t3" style="width:65px;"><tr>
<td class="t1"><div style="font-size:0px;"><img class="t0" style="display:block;border:0;height:auto;width:100%;Margin:0;max-width:100%;" width="55" height="55" alt="" src="./images/2.png"/></div></td><td class="t2" style="width:10px;" width="10"></td>
</tr></table>
</td><td class="t9" valign="top">
<div class="t6" style="mso-line-height-rule:exactly;mso-line-height-alt:7px;line-height:7px;font-size:1px;display:block;">&nbsp;&nbsp;</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="t8" style="width:auto;"><tr>
<td class="t7" style="padding:0 10px 0 10px;"><h1 class="t5" style="margin:0;Margin:0;font-family:Inter,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:40px;font-weight:400;font-style:normal;font-size:55px;text-decoration:none;text-transform:none;letter-spacing:-1px;direction:ltr;color:#FFFFFF;text-align:left;mso-line-height-rule:exactly;mso-text-raise:-4px;">ASTRA</h1></td>
</tr></table>
</td>
<td></td></tr>
</table></div></div></td>
</tr></table>
</td>
</tr></table>
</td></tr><tr><td><div class="t19" style="mso-line-height-rule:exactly;mso-line-height-alt:48px;line-height:48px;font-size:1px;display:block;">&nbsp;&nbsp;</div></td></tr><tr><td align="center">
<table class="t23" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="504" class="t22" style="width:504px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t22" style="width:504px;">
<!--<![endif]-->
<table class="t21" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t20"><h1 class="t18" style="margin:0;Margin:0;font-family:Inter,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:40px;font-weight:700;font-style:normal;font-size:34px;text-decoration:none;text-transform:none;letter-spacing:-1px;direction:ltr;color:#FFFFFF;text-align:left;mso-line-height-rule:exactly;mso-text-raise:2px;">{podcast_title}</h1></td>
</tr></table>
</td>
</tr></table>
</td></tr><tr><td align="center">
<table class="t28" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="504" class="t27" style="width:504px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t27" style="width:504px;">
<!--<![endif]-->
<table class="t26" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t25"><h1 class="t24" style="margin:0;Margin:0;font-family:Inter,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:40px;font-weight:700;font-style:normal;font-size:34px;text-decoration:none;text-transform:none;letter-spacing:-1px;direction:ltr;color:#67E8F9;text-align:left;mso-line-height-rule:exactly;mso-text-raise:2px;">Episode {podcast_num}</h1></td>
</tr></table>
</td>
</tr></table>
</td></tr></table></td>
</tr></table>
</td>
</tr></table>
</td></tr><tr><td align="center">
<table class="t150" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="600" class="t149" style="background-color:#FFFFFF;width:600px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t149" style="background-color:#FFFFFF;width:600px;">
<!--<![endif]-->
<table class="t148" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t147" style="padding:48px 48px 48px 48px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100% !important;"><tr><td align="center">
<table class="t54" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="504" class="t53" style="background-color:#FFFFFF;width:504px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t53" style="background-color:#FFFFFF;width:504px;">
<!--<![endif]-->
<table class="t52" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t51"><div class="t50" style="width:100%;text-align:left;"><div class="t49" style="display:inline-block;"><table class="t48" role="presentation" cellpadding="0" cellspacing="0" align="left" valign="top">
<tr class="t47"><td></td><td class="t46" width="504" valign="top">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="t45" style="width:100%;"><tr>
<td class="t44"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100% !important;"><tr><td align="center">
<table class="t37" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="504" class="t36" style="width:504px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t36" style="width:504px;">
<!--<![endif]-->
<table class="t35" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t34"><h1 class="t33" style="margin:0;Margin:0;font-family:Inter,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:22px;font-weight:700;font-style:normal;font-size:18px;text-decoration:none;text-transform:none;letter-spacing:-0.4px;direction:ltr;color:#0E1012;text-align:left;mso-line-height-rule:exactly;mso-text-raise:1px;">{title_1}</h1></td>
</tr></table>
</td>
</tr></table>
</td></tr><tr><td><div class="t39" style="mso-line-height-rule:exactly;mso-line-height-alt:10px;line-height:10px;font-size:1px;display:block;">&nbsp;&nbsp;</div></td></tr><tr><td align="center">
<table class="t43" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="504" class="t42" style="width:504px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t42" style="width:504px;">
<!--<![endif]-->
<table class="t41" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t40"><p class="t38" style="margin:0;Margin:0;font-family:Inter,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:17px;font-weight:400;font-style:normal;font-size:13px;text-decoration:none;text-transform:none;letter-spacing:-0.2px;direction:ltr;color:#333840;text-align:left;mso-line-height-rule:exactly;mso-text-raise:1px;">{description_1}</p></td>
</tr></table>
</td>
</tr></table>
</td></tr></table></td>
</tr></table>
</td>
<td></td></tr>
</table></div></div></td>
</tr></table>
</td>
</tr></table>
</td></tr><tr><td><div class="t73" style="mso-line-height-rule:exactly;mso-line-height-alt:48px;line-height:48px;font-size:1px;display:block;">&nbsp;&nbsp;</div></td></tr><tr><td align="center">
<table class="t77" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="504" class="t76" style="background-color:#FFFFFF;width:504px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t76" style="background-color:#FFFFFF;width:504px;">
<!--<![endif]-->
<table class="t75" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t74"><div class="t72" style="width:100%;text-align:left;"><div class="t71" style="display:inline-block;"><table class="t70" role="presentation" cellpadding="0" cellspacing="0" align="left" valign="top">
<tr class="t69"><td></td><td class="t68" width="504" valign="top">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="t67" style="width:100%;"><tr>
<td class="t66"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100% !important;"><tr><td align="left">
<table class="t59" role="presentation" cellpadding="0" cellspacing="0" style="Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="219" class="t58" style="width:219px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t58" style="width:219px;">
<!--<![endif]-->
<table class="t57" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t56"><h1 class="t55" style="margin:0;Margin:0;font-family:Inter,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:22px;font-weight:700;font-style:normal;font-size:18px;text-decoration:none;text-transform:none;letter-spacing:-0.4px;direction:ltr;color:#0E1012;text-align:left;mso-line-height-rule:exactly;mso-text-raise:1px;">{title_2}</h1></td>
</tr></table>
</td>
</tr></table>
</td></tr><tr><td><div class="t61" style="mso-line-height-rule:exactly;mso-line-height-alt:10px;line-height:10px;font-size:1px;display:block;">&nbsp;&nbsp;</div></td></tr><tr><td align="center">
<table class="t65" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="504" class="t64" style="width:504px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t64" style="width:504px;">
<!--<![endif]-->
<table class="t63" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t62"><p class="t60" style="margin:0;Margin:0;font-family:Inter,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:17px;font-weight:400;font-style:normal;font-size:13px;text-decoration:none;text-transform:none;letter-spacing:-0.2px;direction:ltr;color:#333840;text-align:left;mso-line-height-rule:exactly;mso-text-raise:1px;">{description_2}</p></td>
</tr></table>
</td>
</tr></table>
</td></tr></table></td>
</tr></table>
</td>
<td></td></tr>
</table></div></div></td>
</tr></table>
</td>
</tr></table>
</td></tr><tr><td><div class="t96" style="mso-line-height-rule:exactly;mso-line-height-alt:48px;line-height:48px;font-size:1px;display:block;">&nbsp;&nbsp;</div></td></tr><tr><td align="center">
<table class="t100" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="504" class="t99" style="background-color:#FFFFFF;width:504px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t99" style="background-color:#FFFFFF;width:504px;">
<!--<![endif]-->
<table class="t98" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t97"><div class="t95" style="width:100%;text-align:left;"><div class="t94" style="display:inline-block;"><table class="t93" role="presentation" cellpadding="0" cellspacing="0" align="left" valign="top">
<tr class="t92"><td></td><td class="t91" width="504" valign="top">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="t90" style="width:100%;"><tr>
<td class="t89"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100% !important;"><tr><td align="center">
<table class="t82" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="504" class="t81" style="width:504px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t81" style="width:504px;">
<!--<![endif]-->
<table class="t80" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t79"><h1 class="t78" style="margin:0;Margin:0;font-family:Inter,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:22px;font-weight:700;font-style:normal;font-size:18px;text-decoration:none;text-transform:none;letter-spacing:-0.4px;direction:ltr;color:#0E1012;text-align:left;mso-line-height-rule:exactly;mso-text-raise:1px;">{title_3}</h1></td>
</tr></table>
</td>
</tr></table>
</td></tr><tr><td><div class="t84" style="mso-line-height-rule:exactly;mso-line-height-alt:10px;line-height:10px;font-size:1px;display:block;">&nbsp;&nbsp;</div></td></tr><tr><td align="center">
<table class="t88" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="504" class="t87" style="width:504px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t87" style="width:504px;">
<!--<![endif]-->
<table class="t86" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t85"><p class="t83" style="margin:0;Margin:0;font-family:Inter,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:17px;font-weight:400;font-style:normal;font-size:13px;text-decoration:none;text-transform:none;letter-spacing:-0.2px;direction:ltr;color:#333840;text-align:left;mso-line-height-rule:exactly;mso-text-raise:1px;">{description_3}</p></td>
</tr></table>
</td>
</tr></table>
</td></tr></table></td>
</tr></table>
</td>
<td></td></tr>
</table></div></div></td>
</tr></table>
</td>
</tr></table>
</td></tr><tr><td><div class="t119" style="mso-line-height-rule:exactly;mso-line-height-alt:48px;line-height:48px;font-size:1px;display:block;">&nbsp;&nbsp;</div></td></tr><tr><td align="center">
<table class="t123" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="504" class="t122" style="background-color:#FFFFFF;width:504px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t122" style="background-color:#FFFFFF;width:504px;">
<!--<![endif]-->
<table class="t121" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t120"><div class="t118" style="width:100%;text-align:left;"><div class="t117" style="display:inline-block;"><table class="t116" role="presentation" cellpadding="0" cellspacing="0" align="left" valign="top">
<tr class="t115"><td></td><td class="t114" width="504" valign="top">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="t113" style="width:100%;"><tr>
<td class="t112"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100% !important;"><tr><td align="center">
<table class="t105" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="504" class="t104" style="width:504px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t104" style="width:504px;">
<!--<![endif]-->
<table class="t103" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t102"><h1 class="t101" style="margin:0;Margin:0;font-family:Inter,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:22px;font-weight:700;font-style:normal;font-size:18px;text-decoration:none;text-transform:none;letter-spacing:-0.4px;direction:ltr;color:#0E1012;text-align:left;mso-line-height-rule:exactly;mso-text-raise:1px;">{title_4}</h1></td>
</tr></table>
</td>
</tr></table>
</td></tr><tr><td><div class="t107" style="mso-line-height-rule:exactly;mso-line-height-alt:10px;line-height:10px;font-size:1px;display:block;">&nbsp;&nbsp;</div></td></tr><tr><td align="center">
<table class="t111" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="504" class="t110" style="width:504px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t110" style="width:504px;">
<!--<![endif]-->
<table class="t109" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t108"><p class="t106" style="margin:0;Margin:0;font-family:Inter,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:17px;font-weight:400;font-style:normal;font-size:13px;text-decoration:none;text-transform:none;letter-spacing:-0.2px;direction:ltr;color:#333840;text-align:left;mso-line-height-rule:exactly;mso-text-raise:1px;">{description_4}</p></td>
</tr></table>
</td>
</tr></table>
</td></tr></table></td>
</tr></table>
</td>
<td></td></tr>
</table></div></div></td>
</tr></table>
</td>
</tr></table>
</td></tr><tr><td><div class="t142" style="mso-line-height-rule:exactly;mso-line-height-alt:48px;line-height:48px;font-size:1px;display:block;">&nbsp;&nbsp;</div></td></tr><tr><td align="center">
<table class="t146" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="504" class="t145" style="background-color:#FFFFFF;width:504px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t145" style="background-color:#FFFFFF;width:504px;">
<!--<![endif]-->
<table class="t144" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t143"><div class="t141" style="width:100%;text-align:left;"><div class="t140" style="display:inline-block;"><table class="t139" role="presentation" cellpadding="0" cellspacing="0" align="left" valign="top">
<tr class="t138"><td></td><td class="t137" width="504" valign="top">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="t136" style="width:100%;"><tr>
<td class="t135"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100% !important;"><tr><td align="center">
<table class="t128" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="504" class="t127" style="width:504px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t127" style="width:504px;">
<!--<![endif]-->
<table class="t126" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t125"><h1 class="t124" style="margin:0;Margin:0;font-family:Inter,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:22px;font-weight:700;font-style:normal;font-size:18px;text-decoration:none;text-transform:none;letter-spacing:-0.4px;direction:ltr;color:#0E1012;text-align:left;mso-line-height-rule:exactly;mso-text-raise:1px;">{title_5}</h1></td>
</tr></table>
</td>
</tr></table>
</td></tr><tr><td><div class="t130" style="mso-line-height-rule:exactly;mso-line-height-alt:10px;line-height:10px;font-size:1px;display:block;">&nbsp;&nbsp;</div></td></tr><tr><td align="center">
<table class="t134" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="504" class="t133" style="width:504px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t133" style="width:504px;">
<!--<![endif]-->
<table class="t132" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t131"><p class="t129" style="margin:0;Margin:0;font-family:Inter,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:17px;font-weight:400;font-style:normal;font-size:13px;text-decoration:none;text-transform:none;letter-spacing:-0.2px;direction:ltr;color:#333840;text-align:left;mso-line-height-rule:exactly;mso-text-raise:1px;">{description_5}</p></td>
</tr></table>
</td>
</tr></table>
</td></tr></table></td>
</tr></table>
</td>
<td></td></tr>
</table></div></div></td>
</tr></table>
</td>
</tr></table>
</td></tr></table></td>
</tr></table>
</td>
</tr></table>
</td></tr><tr><td align="center">
<table class="t193" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="600" class="t192" style="background-color:#FFFFFF;width:600px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t192" style="background-color:#FFFFFF;width:600px;">
<!--<![endif]-->
<table class="t191" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t190" style="padding:32px 48px 32px 48px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100% !important;"><tr><td align="center">
<table class="t176" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="504" class="t175" style="border-bottom:1px solid #EBEBEB;width:504px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t175" style="border-bottom:1px solid #EBEBEB;width:504px;">
<!--<![endif]-->
<table class="t174" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t173" style="padding:0 0 20px 0;"><div class="t172" style="width:100%;text-align:left;"><div class="t171" style="display:inline-block;"><table class="t170" role="presentation" cellpadding="0" cellspacing="0" align="left" valign="middle">
<tr class="t169"><td></td><td class="t155" width="50" valign="middle">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="t154" style="width:50px;"><tr>
<td class="t152"><div style="font-size:0px;"><img class="t151" style="display:block;border:0;height:auto;width:100%;Margin:0;max-width:100%;" width="40" height="40" alt="" src="./images/1.png"/></div></td><td class="t153" style="width:10px;" width="10"></td>
</tr></table>
</td><td class="t168" width="454" valign="middle">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="t167" style="width:100%;"><tr>
<td class="t166"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100% !important;"><tr><td align="center">
<table class="t160" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="454" class="t159" style="width:454px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t159" style="width:454px;">
<!--<![endif]-->
<table class="t158" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t157"><p class="t156" style="margin:0;Margin:0;font-family:Lato,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:22px;font-weight:400;font-style:normal;font-size:10px;text-decoration:none;text-transform:none;direction:ltr;color:#333333;text-align:center;mso-line-height-rule:exactly;mso-text-raise:4px;">You are recieving this email because you have an active account on Astra.</p></td>
</tr></table>
</td>
</tr></table>
</td></tr><tr><td align="center">
<table class="t165" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td class="t164" style="background-color:#FFFFFF;width:auto;">
<![endif]-->
<!--[if !mso]>-->
<td class="t164" style="background-color:#FFFFFF;width:auto;">
<!--<![endif]-->
<table class="t163" role="presentation" cellpadding="0" cellspacing="0" style="width:auto;"><tr>
<td class="t162" style="text-align:center;line-height:24px;mso-line-height-rule:exactly;mso-text-raise:4px;padding:0 10px 0 10px;"><span class="t161" style="display:block;margin:0;Margin:0;font-family:Lato,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:24px;font-weight:700;font-style:normal;font-size:10px;text-decoration:none;direction:ltr;color:#67E8F9;text-align:center;mso-line-height-rule:exactly;mso-text-raise:4px;">Deactivate Account</span></td>
</tr></table>
</td>
</tr></table>
</td></tr></table></td>
</tr></table>
</td>
<td></td></tr>
</table></div></div></td>
</tr></table>
</td>
</tr></table>
</td></tr><tr><td><div class="t177" style="mso-line-height-rule:exactly;mso-line-height-alt:28px;line-height:28px;font-size:1px;display:block;">&nbsp;&nbsp;</div></td></tr><tr><td><div class="t179" style="mso-line-height-rule:exactly;mso-line-height-alt:4px;line-height:4px;font-size:1px;display:block;">&nbsp;&nbsp;</div></td></tr><tr><td align="center">
<table class="t183" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="504" class="t182" style="width:504px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t182" style="width:504px;">
<!--<![endif]-->
<table class="t181" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t180"><p class="t178" style="margin:0;Margin:0;font-family:Inter,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:18px;font-weight:400;font-style:normal;font-size:13px;text-decoration:none;text-transform:none;letter-spacing:-0.2px;direction:ltr;color:#9F9DA8;text-align:left;mso-line-height-rule:exactly;mso-text-raise:2px;">Copyright © 2025 Astra, all rights reserved.</p></td>
</tr></table>
</td>
</tr></table>
</td></tr><tr><td><div class="t185" style="mso-line-height-rule:exactly;mso-line-height-alt:4px;line-height:4px;font-size:1px;display:block;">&nbsp;&nbsp;</div></td></tr><tr><td align="center">
<table class="t189" role="presentation" cellpadding="0" cellspacing="0" style="Margin-left:auto;Margin-right:auto;">
<tr>
<!--[if mso]>
<td width="504" class="t188" style="width:504px;">
<![endif]-->
<!--[if !mso]>-->
<td class="t188" style="width:504px;">
<!--<![endif]-->
<table class="t187" role="presentation" cellpadding="0" cellspacing="0" width="100%" style="width:100%;"><tr>
<td class="t186"><p class="t184" style="margin:0;Margin:0;font-family:Inter,BlinkMacSystemFont,Segoe UI,Helvetica Neue,Arial,sans-serif;line-height:18px;font-weight:400;font-style:normal;font-size:13px;text-decoration:none;text-transform:none;letter-spacing:-0.2px;direction:ltr;color:#9297A0;text-align:left;mso-line-height-rule:exactly;mso-text-raise:2px;">Durham, North Carolina, 27708 USA</p></td>
</tr></table>
</td>
</tr></table>
</td></tr></table></td>
</tr></table>
</td>
</tr></table>
</td></tr></table></td></tr></table></div><div class="gmail-fix" style="display: none; white-space: nowrap; font: 15px courier; line-height: 0;">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</div></body>
</html>
    """

    msg.attach(MIMEText(email_body, 'html'))

    # Attach the podcast file
    if os.path.exists(podcast_file_path):
        with open(podcast_file_path, 'rb') as podcast_file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(podcast_file.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="{os.path.basename(podcast_file_path)}"'
            )
            msg.attach(part)

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Example usage
if __name__ == "__main__":
    recipient = "customer@example.com"
    title = "The Future of AI in Healthcare"
    description = "In this week's podcast, we explore groundbreaking AI technologies reshaping the healthcare industry."
    podcast_path = "path_to_podcast.mp3"
    updates = "We've added new features to make it easier to discover personalized content. Check out the latest updates in your app!"

    send_email(recipient, title, description, podcast_path, updates)
