function awsmfa
    set creds (/Users/dillon.isaacs_tse/aws-mfa-session.py --output json) && set -xg AWS_ACCESS_KEY_ID (echo $creds | jq -r .AWS_ACCESS_KEY_ID) && set -xg AWS_SECRET_ACCESS_KEY (echo $creds | jq -r .AWS_SECRET_ACCESS_KEY) && set -xg AWS_SESSION_TOKEN (echo $creds | jq -r .AWS_SESSION_TOKEN)
end
