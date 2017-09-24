#!/usr/bin/Rscript

library(ggplot2)
# files <- rev(list.files("data", recursive = TRUE, full.names = TRUE))[1:3]
files <- rev(list.files("data", recursive = TRUE, full.names = TRUE))
df <- do.call(rbind, lapply(files, function (x) read.csv(x, header = FALSE)))
names(df) <- c("dt", "temp", "o_temp", "temp1", "temp2", "humidity", "o_humidity")

df$dt <- as.POSIXct(strptime(df$dt, "%Y-%m-%d %H:%M:%S"))
df <- df[order(df$dt), ]
df <- tail(df, 288)  # Last 48 hours

plot.df <- rbind(data.frame(dt = df$dt, temp = df$temp, variable = "Ambient"),
                 data.frame(dt = df$dt, temp = df$o_temp, variable = "Outdoors"),
                 data.frame(dt = df$dt, temp = df$temp1, variable = "Fermenter 1"),
                 data.frame(dt = df$dt, temp = df$temp2, variable = "Fermenter 2"))
g <- ggplot(plot.df, aes(dt, temp)) + geom_line(aes(color = variable)) +
  xlab("") + ylab("°C") +
  theme(axis.text = element_text(family = "Roboto", size = 16),
        axis.text.x = element_text(angle = 45, hjust = 1),
        axis.title = element_text(family = "Roboto", size = 16),
        legend.text = element_text(family = "Roboto", size = 22),
        legend.position = "bottom", legend.title = element_blank())

png(filename = "/home/pi/swamptemp.github.io/history.png",
    height = 400, width = 800)
plot(g)
dev.off()

plot.df <- rbind(data.frame(dt = df$dt, humidity = df$humidity,
                            variable = "Indoor humidity"),
                 data.frame(dt = df$dt, humidity = df$o_humidity,
                            variable = "Outdoor humidity"))

g <- ggplot(plot.df, aes(dt, humidity)) + geom_line(aes(color = variable)) +
  xlab("") + ylab("Humidity (%)") +
  theme(axis.text = element_text(family = "Roboto", size = 16),
        axis.text.x = element_text(angle = 45, hjust = 1),
        axis.title = element_text(family = "Roboto", size = 16),
        legend.text = element_text(family = "Roboto", size = 22),
        legend.position = "bottom", legend.title = element_blank())
png(filename = "/home/pi/swamptemp.github.io/humidity.png",
    height = 400, width = 800)
plot(g)
dev.off()
