# Copyright (c) 2016-2023 SUSE LLC.
# Licensed under the terms of the MIT license.
require 'redis'
require 'nokogiri'
require 'open-uri'

class CodeCoverage
  def initialize(redis_host, redis_username, redis_password)
    @database = Redis.new(:host => redis_host, :username => redis_username, :password => redis_password)
  end

  def push_feature_coverage(feature_name)
    tree = Nokogiri::HTML(URI.open("http://#{$server.full_hostname}/pub/jacoco-#{feature_name}.xml"))
    tree.xpath("//package").each { |package|
      package_name = package.css("name")
      package.xpath("//sourcefile").each { |sourcefile|
        sourcefile_name = sourcefile.css("name")
        counter_class = sourcefile.xpath("./counter[@type='CLASS']")
        if not counter_class.nil? and counter_class.css("covered").to_i > 0
          puts("> #{package_name}/#{sourcefile_name} : #{feature_name}")
          @database.sadd("#{package_name}/#{sourcefile_name}", feature_name)
        end
      }
    }
  end

  def jacoco_dump(feature_name, html = false, xml = true, source = false)
    cli = "java -jar /tmp/jacococli.jar"
    html_report = html ? "--html /srv/www/htdocs/pub/jacoco-#{feature_name}" : ""
    xml_report = xml ? "--xml /srv/www/htdocs/pub/jacoco-#{feature_name}.xml" : ""
    sourcefiles = source ? "--sourcefiles /tmp/uyuni-master/java/code/src" : ""
    classfiles = "--classfiles /srv/tomcat/webapps/rhn/WEB-INF/lib"
    dump_path = "/tmp/jacoco-#{feature_name}.exec"
    $server.run("#{cli} dump --address localhost --destfile #{dump_path} --port 6300 --reset")
    $server.run("#{cli} report #{dump_path} #{html_report} #{xml_report} #{sourcefiles} #{classfiles}")
  end
end
