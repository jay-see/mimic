This python3 script will monitor the activity of an X influencer of your
choosing every 45 seconds and post whenever the influencer posts.  Currently,
the code works for new posts ONLY, not for replies or retweets or likes.
I tested successfully on Windows Powershell.

1 - Copy all the files in this folder.

2 - In the working directory, run:
        pip install selenium
        pip install -r requirements.txt

3 - Edit the .env file to add your X credentials.  Posts will be posted from this account.

4 - Then run:
       python3 mimic.py

It will prompt you to enter the X influencer's username to monitor.
For testing, I recommend entering the username of an account you control,
and create a new post from that account, so you don't have to wait for the 
influencer to post.

Be patient with this tool since it checks for new posts every 45 seconds.
