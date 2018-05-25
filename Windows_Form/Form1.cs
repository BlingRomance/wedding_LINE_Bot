using System;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;
using MySql.Data.MySqlClient;

namespace BingBride
{
    public partial class Form1 : Form
    {
        int speed = 6;
        List<string> content = new List<string>();
        int count = 0;
        Random random1 = new Random();
        PictureBox picture_box = new PictureBox();
        int imgur_count = 0;
        List<string> link = new List<string>();
        int r = 0;
        List<string> local_img = new List<string>();
        String path = "";
        AxWMPLib.AxWindowsMediaPlayer music_player;
        AxWMPLib.AxWindowsMediaPlayer media_player;
        int rnum = 0;
        int play_status = 0;

        /**
         * Initialization and create picture_box, media_player and music_player.
         *
         * picture_box for show the picture from the LINE Bot.
         * media_player for playing wedding mv.
         * music_player for playing backgrond music.
         */
        public Form1()
        {
            // initialization
            InitializeComponent();
            this.DoubleBuffered = true;

            path = System.IO.Directory.GetCurrentDirectory();

            // add defult picture
            local_img.Add(path + @"\bnb\2jXNJAo.jpg");
            local_img.Add(path + @"\bnb\zVgqz9n.jpg");
            
            picture_box = new System.Windows.Forms.PictureBox();
            picture_box.Location = new Point(0, label1.Height + 10);
            picture_box.Size = new System.Drawing.Size(Screen.PrimaryScreen.Bounds.Width, Screen.PrimaryScreen.Bounds.Height - (label1.Height + 50));
            picture_box.SizeMode = PictureBoxSizeMode.Zoom;
            Controls.Add(picture_box);
            
            media_player = new AxWMPLib.AxWindowsMediaPlayer();
            media_player.Location = new Point(0, label1.Height + 10);
            media_player.Size = new System.Drawing.Size(Screen.PrimaryScreen.Bounds.Width, Screen.PrimaryScreen.Bounds.Height - 25);
            media_player.KeyDownEvent += axWindowsMediaPlayer_KeyDownEvent;
            Controls.Add(media_player);
            media_player.Visible = false;

            music_player = new AxWMPLib.AxWindowsMediaPlayer();
            music_player.Location = new Point(-Screen.PrimaryScreen.Bounds.Width, -Screen.PrimaryScreen.Bounds.Height);
            music_player.KeyDownEvent += axWindowsMediaPlayer_KeyDownEvent;
            music_player.MediaChange += axWindowsMediaPlayer_MediaChange;
            Controls.Add(music_player);

            this.ShowInTaskbar = false;
        }

        /**
         * Run the timer and backgroud music.
         */
        private void Form1_Load(object sender, EventArgs e)
        {
            timer2.Interval = 20;
            timer2.Start();

            rnum = random1.Next(1, 4);
            Console.WriteLine(rnum);
            music_player.URL = path + @"\music\" + rnum.ToString() + @".mp3";
            music_player.settings.volume = 100;

            timer1.Interval = 5000;
            timer1.Start();
        }

        /**
         * Get pictures link from database and show it.
         */
        private void timer1_Tick(object sender, EventArgs e)
        {

            if (imgur_count != 0)
            {
                picture_box.LoadAsync(link[imgur_count - 1]);
                imgur_count--;
            }
            else
            {
                try
                {
                    if (r != 0)
                    {
                        r = 0;
                    }
                    else
                    {
                        r = 1;
                    }
                    picture_box.LoadAsync(local_img[r]);
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.ToString());
                }

                link.Clear();

                MySqlConnection conn_image = new MySqlConnection("server={sql_server_ip}; port=3306; user=bnb_c; password=12345678; database=bnb_wedding");
                try
                {
                    conn_image.Open();
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.ToString());
                }
                String blessing_image = "SELECT * FROM wedding_image WHERE wedding_image_timestamp >= '" + DateTime.Now.ToString("yyyy-MM-dd") + "'";
                MySqlCommand blessing_command_image = new MySqlCommand(blessing_image, conn_image);

                try
                {
                    MySqlDataReader blessing_reader_image = blessing_command_image.ExecuteReader();
                    while (blessing_reader_image.Read())
                    {
                        link.Add(blessing_reader_image.GetString(1));
                        imgur_count++;
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.ToString());
                }

                conn_image.Close();
            }
        }

        /**
         * Get blessings content from database and use marquee way to show it.
         */
        private void timer2_Tick(object sender, EventArgs e)
        {
            if (play_status == 1)
            {
                music_player.Ctlcontrols.play();
                play_status = 0;
            }

            if (label1.Left < 0 && (Math.Abs(label1.Left) > label1.Width))
            {
                label1.Left = this.Width;
                if (count <= content.Count && count != 0)
                {
                    label1.Text = content[count - 1];
                    count--;
                }
                else
                {
                    try
                    {
                        label1.Text = content[random1.Next(0, content.Count)];
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex.ToString());
                    }
                    
                    content.Clear();

                    MySqlConnection conn = new MySqlConnection("server={sql_server_ip}; port=3306; user=bnb_c; password=12345678; database=bnb_wedding");
                    try
                    {
                        conn.Open();
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex.ToString());
                    }
                    String blessing_text = "SELECT * FROM wedding_blessing WHERE wedding_blessing_timestamp >= '" + DateTime.Now.ToString("yyyy-MM-dd") + "'";
                    MySqlCommand blessing_command = new MySqlCommand(blessing_text, conn);
                    try
                    {
                        MySqlDataReader blessing_reader = blessing_command.ExecuteReader();
                        while (blessing_reader.Read())
                        {
                            content.Add(blessing_reader.GetString(1) + "：" + blessing_reader.GetString(2));
                            count++;
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex.ToString());
                    }
                    
                    conn.Close();
                }
                
                label1.ForeColor = Color.Red;
            }

            label1.Left -= speed;
        }

        /**
         * The hot key for Form to play the media_player/music_player.
         */
        private void Form1_KeyDown(object sender, KeyEventArgs e)
        {
            switch (e.KeyCode)
            {
                case Keys.F1:
                    this.Close();
                    break;

                case Keys.F2:
                    if (this.TopMost == false)
                    {
                        this.FormBorderStyle = FormBorderStyle.FixedSingle;
                        this.WindowState = FormWindowState.Normal;
                        this.TopMost = true;
                    }
                    else
                    {
                        this.FormBorderStyle = FormBorderStyle.None;
                        this.WindowState = FormWindowState.Maximized;
                        this.TopMost = false;
                    }
                    break;

                case Keys.F3:
                    picture_box.Visible = true;
                    try
                    {
                        media_player.Ctlcontrols.stop();
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex.ToString());
                    }
                    media_player.Visible = false;
                    music_player.URL = path + @"\music\" + random1.Next(1, 4).ToString() + @".mp3";
                    music_player.Ctlcontrols.play();
                    break;

                case Keys.F4:
                    try
                    {
                        music_player.Ctlcontrols.stop();
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex.ToString());
                    }
                    picture_box.Visible = false;
                    media_player.Visible = true;
                    media_player.URL = path + @"\bnb\WEDDING.wmv";
                    break;

                case Keys.F5:
                    music_player.Ctlcontrols.stop();
                    music_player.URL = path + @"\music\Wherever_You_Go.mp3";
                    play_status = 1;
                    break;

                case Keys.F12:
                    try
                    {
                        music_player.Ctlcontrols.stop();
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex.ToString());
                    }
                    picture_box.Visible = false;
                    media_player.Visible = true;
                    media_player.URL = path + @"\bnb\blessing.wmv";
                    break;
            }
            
        }

        /**
         * The hot key for MediaPlayer to play the media_player/music_player.
         */
        private void axWindowsMediaPlayer_KeyDownEvent(object sender, AxWMPLib._WMPOCXEvents_KeyDownEvent e)
        {
            switch (e.nKeyCode)
            {
                case 112: // F1
                    this.Close();
                    break;

                case 113: // F2
                    if (this.TopMost == false)
                    {
                        this.FormBorderStyle = FormBorderStyle.FixedSingle;
                        this.WindowState = FormWindowState.Normal;
                        this.TopMost = true;
                    }
                    else
                    {
                        this.FormBorderStyle = FormBorderStyle.None;
                        this.WindowState = FormWindowState.Maximized;
                        this.TopMost = false;
                    }
                    break;

                case 114: // F3
                    picture_box.Visible = true;
                    try
                    {
                        media_player.Ctlcontrols.stop();
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex.ToString());
                    }
                    media_player.Visible = false;
                    music_player.URL = path + @"\music\" + random1.Next(1, 4).ToString() + @".mp3";
                    music_player.Ctlcontrols.play();
                    break;

                case 115: // F4
                    try
                    {
                        music_player.Ctlcontrols.stop();
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex.ToString());
                    }
                    picture_box.Visible = false;
                    media_player.Visible = true;
                    media_player.URL = path + @"\bnb\WEDDING.wmv";
                    break;

                case 116: // F5
                    music_player.Ctlcontrols.stop();
                    music_player.URL = path + @"\music\Wherever_You_Go.mp3";
                    play_status = 1;
                    break;

                case 121: // F10
                    break;

                case 123: // F12
                    try
                    {
                        music_player.Ctlcontrols.stop();
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex.ToString());
                    }
                    picture_box.Visible = false;
                    media_player.Visible = true;
                    media_player.URL = path + @"\bnb\blessing.wmv";
                    break;
            }
        }

        private void axWindowsMediaPlayer_MediaChange(object sender, AxWMPLib._WMPOCXEvents_MediaChangeEvent e)
        {
            if (music_player.status == "完成")
            {
                int num = random1.Next(1, 4);
                while (rnum == num)
                {
                    num = random1.Next(1, 4);
                }
                rnum = num;
                music_player.Ctlcontrols.stop();
                music_player.URL = path + @"\music\" + rnum.ToString() + @".mp3";
                play_status = 1;
            }
        }
    }
}
